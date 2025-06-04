//Init information
param subscriptionName string
param subscriptionId string
param resourceGroupName string
param resourceGroupNetworkName string
param identityName string
param envName string
param keyVault string
param containerRegistry string
param workloadProfileName string

//KV Secrets and Parameter
param containerAppEnvironment string

//Container configuration
param imageArtifact string
param containerResoucerCPU string
param containerResoucerMemory string
param containerResoucerStorage string
param containerRevMode string

// ------------------
// RESOURCES
// ------------------
@description('Get existing user assigned identity resource details')
resource userAssignedIdentity 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-07-31-preview' existing = {
  name: identityName
  scope: resourceGroup(resourceGroupNetworkName)
}

@description('Get existing app env resource details')
resource containerAppsEnvironment 'Microsoft.App/managedEnvironments@2022-03-01' existing = {
  name: envName
}

//* Microservice
resource ipsgeneratorweb 'Microsoft.App/containerApps@2024-03-01' = {
  name: 'ipsgenerator-web'
  location: resourceGroup().location
  tags: {
    Application: 'IPS Generator Web'
    Department: 'ITOps'
    Environment: subscriptionName
    ProductOwner: 'ITOperations@aviso.ca'
  }
  properties: {
    managedEnvironmentId: containerAppsEnvironment.id
    environmentId: containerAppsEnvironment.id
    workloadProfileName: workloadProfileName
    configuration: {
      secrets: null
      activeRevisionsMode: containerRevMode
      ingress: {
        external: true
        targetPort: 8000
        exposedPort: 0
        transport: 'Auto'
        traffic: [
          {
            weight: 100
            latestRevision: true
          }
        ]
        customDomains: []
        allowInsecure: false
        clientCertificateMode: 'Ignore'
      }
      registries: [
        {
          server: containerRegistry
          identity: userAssignedIdentity.id
        }
      ]
      dapr: null
      maxInactiveRevisions: 100
    }
    template: {
      containers: [
        {
          image: imageArtifact
          name: 'ips-generator-web'
          env: [
            {
              name: 'ENVIRONMENT'
              value: containerAppEnvironment
            }
          ]
          resources: {
            cpu: json(containerResoucerCPU)
            memory: containerResoucerMemory
          }
          probes: []
        }
      ]
      scale: {
        minReplicas: 1
        maxReplicas: 10
      }
    }
  }
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: {
      '${userAssignedIdentity.id}': {}
    }
  }
}
