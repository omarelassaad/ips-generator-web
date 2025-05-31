using './main.bicep'

param subscriptionName = '$(SUBSCRIPTION_NAME)'
param subscriptionId = '$(SUBSCRIPTION_ID)'
param resourceGroupName = '$(RG_NAME)'
param resourceGroupNetworkName = '$(RG_NETWORK_NAME)'
param identityName = '$(IDENTITY_NAME)'
param envName = '$(CONTAINER_APP_ENV)'
param keyVault = '$(KEY_VAULT_URL)'
param containerRegistry = '$(ACR_NONPROD_URL)'
param workloadProfileName = '$(WORKLOADPROFILE_NAME)'

param containerAppEnvironment = 'Staging'

param imageArtifact = '${containerRegistry}/ips-generator-web/test/ips-generator-web:1.0.0-20250529.10'
param containerResoucerCPU = '0.75'
param containerResoucerMemory = '1.5Gi'
param containerResoucerStorage = '2Gi'
param containerRevMode = 'Single'
