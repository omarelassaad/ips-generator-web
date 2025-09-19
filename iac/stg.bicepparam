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

param sqlDbName = 'sqldb-ips-generator-dev-cc-01'
param sqlSvrName = 'sql-nxgcae-dev-cc-01.database.windows.net'
param sqlUsrName = 'uai_ips_generator_dev_cc_01_LOCAL'
param sqlPswdKV = '${keyVault}/sqlPswdIps'

param imageArtifact = '${containerRegistry}/ips-generator-web/test/ips-generator-web:1.0.0-20250529.10'

param cpu = '$(IPS_GENERATOR_WEB_CPU)'
param ram = '$(IPS_GENERATOR_WEB_RAM)'
param minReplicas = '$(IPS_GENERATOR_WEB_MINREP)'
param maxReplicas = '$(IPS_GENERATOR_WEB_MAXREP)'
param concurrentRequests = '$(IPS_GENERATOR_WEB_CCR)'

param containerResoucerStorage = '2Gi'
param containerRevMode = 'Single'
