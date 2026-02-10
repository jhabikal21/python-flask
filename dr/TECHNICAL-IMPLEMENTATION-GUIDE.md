# Azure DR Implementation Guide: UK South → UAE North

**Technical Implementation Reference**  
**Primary Region:** UK South (uksouth)  
**DR Region:** UAE North (uaenorth)  
**Network Latency:** ~229ms RTT  
**Region Pair Status:** Non-paired regions

---

## Critical Pre-Implementation Questions

### Infrastructure & Networking

**Q1. Network Architecture**
- [ ] What is your current VNet CIDR range in UK South?
- [ ] Will you use separate VNet in UAE North or VNet peering?
- [ ] Do you have ExpressRoute circuits? If yes, where are they terminated?
- [ ] What is your current DNS strategy (Azure DNS, custom DNS)?
- [ ] Do you use Azure Firewall, NVAs, or third-party firewalls?
- [ ] What are your NSG rules and application security groups?
- [ ] Do you have VPN Gateway for site-to-site connectivity?

**Q2. Compute Resources**
- [ ] What VM SKUs are you currently using in UK South?
  - List all SKUs: _________________
- [ ] Do you use Availability Sets or Availability Zones in UK South?
- [ ] Are you using Azure Kubernetes Service (AKS)? If yes, what version?
- [ ] Do you have Azure App Service plans? What tier (Basic, Standard, Premium)?
- [ ] Are you using Azure Functions? What hosting plan (Consumption, Premium, Dedicated)?
- [ ] Do you use VM Scale Sets (VMSS)? What are the min/max instance counts?
- [ ] Are any VMs using managed disks with specific performance tiers (Standard, Premium, Ultra)?

**Q3. Data Services**
- [ ] What databases are you running?
  - Azure SQL Database: Yes/No - If yes, what tier? _________________
  - Azure SQL Managed Instance: Yes/No
  - Cosmos DB: Yes/No - If yes, consistency level? _________________
  - MySQL/PostgreSQL: Yes/No - Single Server or Flexible Server?
  - Azure Database for MariaDB: Yes/No
- [ ] What is your current database size and growth rate?
- [ ] Do you use geo-replication for any databases currently?
- [ ] What is your acceptable data loss window (RPO)?
  - < 5 minutes / 5-15 minutes / 15-60 minutes / > 1 hour
- [ ] What storage accounts do you have?
  - Storage account names: _________________
  - Replication type (LRS, ZRS, GRS, RA-GRS): _________________
  - Blob access tiers (Hot, Cool, Archive): _________________

**Q4. Application Architecture**
- [ ] Do you use Azure OpenAI Service? **CRITICAL: Not available in UAE North**
  - If yes, what models? _________________
  - Can you keep AI workloads in UK South/UK West?
- [ ] Do you use Azure Cognitive Services? Which ones?
  - Face API / LUIS / QnA Maker / Translator / Other: _________________
- [ ] Do you use Azure Machine Learning?
- [ ] Do you use Azure Databricks?
- [ ] Do you use Azure Synapse Analytics?
- [ ] What message queues/event systems do you use?
  - Service Bus: Yes/No - Premium tier? _________________
  - Event Hubs: Yes/No - Throughput units? _________________
  - Event Grid: Yes/No
  - Storage Queues: Yes/No
- [ ] Do you use Azure Cache for Redis? What tier?
- [ ] Do you use Azure API Management? What tier?

**Q5. Identity & Security**
- [ ] Do you use Azure AD B2C or Azure AD B2B?
- [ ] Do you use Managed Identities for authentication?
- [ ] Do you use Key Vault? How many secrets/keys/certificates?
- [ ] Do you use Azure Sentinel for SIEM?
- [ ] Do you use Azure Defender/Microsoft Defender for Cloud?
- [ ] What compliance certifications do you need?
  - ISO 27001 / SOC 2 / PCI DSS / HIPAA / Other: _________________

**Q6. Monitoring & Operations**
- [ ] What monitoring tools are you using?
  - Azure Monitor / Application Insights / Log Analytics
- [ ] Do you have custom dashboards or workbooks?
- [ ] What are your alert rules and action groups?
- [ ] Do you use Azure Automation runbooks?
- [ ] What is your backup strategy?
  - Azure Backup: Yes/No - Retention period? _________________
  - Custom backup scripts: Yes/No

**Q7. DevOps & Deployment**
- [ ] What is your deployment method?
  - Azure DevOps Pipelines / GitHub Actions / Jenkins / Other
- [ ] Do you use Infrastructure as Code?
  - Terraform / ARM Templates / Bicep / Pulumi
- [ ] Do you use GitOps (ArgoCD, Flux)?
- [ ] How are secrets managed in deployments?
  - Key Vault references / Azure DevOps variable groups / GitHub Secrets

**Q8. Compliance & Data Residency**
- [ ] What type of data do you process?
  - Personal data (GDPR) / Financial data / Healthcare data / Other
- [ ] Do you have data residency requirements?
- [ ] Have you completed a Data Protection Impact Assessment (DPIA)?
- [ ] Do you have UK GDPR compliance documentation?
- [ ] Are you prepared for UAE PDPL compliance requirements?

---

## Technical Implementation Tasks

### Phase 1: Network Foundation (Week 1)

#### Task 1.1: UAE North VNet Setup
```bash
# Create resource group
az group create \
  --name rg-dr-uaenorth-prod \
  --location uaenorth

# Create VNet with non-overlapping CIDR
az network vnet create \
  --resource-group rg-dr-uaenorth-prod \
  --name vnet-dr-uaenorth \
  --address-prefix 10.1.0.0/16 \
  --subnet-name subnet-app \
  --subnet-prefix 10.1.1.0/24
```

**Checklist:**
- [ ] Design VNet CIDR that doesn't overlap with UK South (10.0.0.0/16)
- [ ] Create subnets for: App tier, Data tier, Management, AKS (if applicable)
- [ ] Document subnet allocation in network diagram
- [ ] Configure subnet delegation if using Azure services (e.g., SQL MI, NetApp Files)

#### Task 1.2: VNet Peering (UK South ↔ UAE North)
```bash
# Create peering from UK South to UAE North
az network vnet peering create \
  --resource-group rg-uksouth-prod \
  --name peer-uksouth-to-uaenorth \
  --vnet-name vnet-uksouth \
  --remote-vnet /subscriptions/{sub-id}/resourceGroups/rg-dr-uaenorth-prod/providers/Microsoft.Network/virtualNetworks/vnet-dr-uaenorth \
  --allow-vnet-access \
  --allow-forwarded-traffic

# Create peering from UAE North to UK South
az network vnet peering create \
  --resource-group rg-dr-uaenorth-prod \
  --name peer-uaenorth-to-uksouth \
  --vnet-name vnet-dr-uaenorth \
  --remote-vnet /subscriptions/{sub-id}/resourceGroups/rg-uksouth-prod/providers/Microsoft.Network/virtualNetworks/vnet-uksouth \
  --allow-vnet-access \
  --allow-forwarded-traffic
```

**Checklist:**
- [ ] Enable VNet peering bidirectionally
- [ ] Test connectivity with test VMs (ping, traceroute)
- [ ] Measure actual latency between regions
- [ ] Configure route tables if using hub-spoke topology
- [ ] Update NSGs to allow cross-region traffic

#### Task 1.3: DNS Configuration
```bash
# Create Azure Private DNS Zone
az network private-dns zone create \
  --resource-group rg-dr-uaenorth-prod \
  --name internal.contoso.com

# Link DNS zone to both VNets
az network private-dns link vnet create \
  --resource-group rg-dr-uaenorth-prod \
  --zone-name internal.contoso.com \
  --name dns-link-uaenorth \
  --virtual-network vnet-dr-uaenorth \
  --registration-enabled true
```

**Checklist:**
- [ ] Decide on DNS strategy: Azure DNS, custom DNS, or hybrid
- [ ] Create Private DNS zones for cross-region name resolution
- [ ] Link DNS zones to both UK South and UAE North VNets
- [ ] Test DNS resolution from both regions
- [ ] Document DNS naming convention for DR resources

#### Task 1.4: Load Balancer & Traffic Manager
```bash
# Create Traffic Manager profile for global load balancing
az network traffic-manager profile create \
  --resource-group rg-global \
  --name tm-app-global \
  --routing-method Priority \
  --unique-dns-name app-contoso-global

# Add UK South endpoint (Priority 1)
az network traffic-manager endpoint create \
  --resource-group rg-global \
  --profile-name tm-app-global \
  --name endpoint-uksouth \
  --type azureEndpoints \
  --target-resource-id /subscriptions/{sub-id}/resourceGroups/rg-uksouth-prod/providers/Microsoft.Network/publicIPAddresses/pip-app-uksouth \
  --priority 1 \
  --endpoint-status Enabled

# Add UAE North endpoint (Priority 2)
az network traffic-manager endpoint create \
  --resource-group rg-global \
  --profile-name tm-app-global \
  --name endpoint-uaenorth \
  --type azureEndpoints \
  --target-resource-id /subscriptions/{sub-id}/resourceGroups/rg-dr-uaenorth-prod/providers/Microsoft.Network/publicIPAddresses/pip-app-uaenorth \
  --priority 2 \
  --endpoint-status Enabled
```

**Checklist:**
- [ ] Choose routing method: Priority (failover) or Performance (active-active)
- [ ] Configure health probes for automatic failover
- [ ] Set up monitoring for Traffic Manager health
- [ ] Test failover by disabling UK South endpoint
- [ ] Update DNS records to point to Traffic Manager FQDN

---

### Phase 2: Storage & Data Replication (Week 1-2)

#### Task 2.1: Storage Account Replication

**Option A: GRS/RA-GRS (Automatic, but limited control)**
```bash
# Convert existing storage to RA-GRS (if not already)
az storage account update \
  --resource-group rg-uksouth-prod \
  --name stuksouthprod \
  --sku Standard_RAGRS

# Note: Secondary location is automatically UK West, NOT UAE North
# For UAE North, you need manual replication
```

**Option B: Manual Replication with AzCopy (Full control)**
```bash
# Create storage account in UAE North
az storage account create \
  --resource-group rg-dr-uaenorth-prod \
  --name stuaenorthdr \
  --location uaenorth \
  --sku Standard_ZRS \
  --kind StorageV2

# Sync blobs from UK South to UAE North (one-time or scheduled)
azcopy sync \
  "https://stuksouthprod.blob.core.windows.net/container?[SAS-UK]" \
  "https://stuaenorthdr.blob.core.windows.net/container?[SAS-UAE]" \
  --recursive
```

**Option C: Azure Data Factory Pipeline (Automated, scheduled)**
```json
{
  "name": "StorageReplicationPipeline",
  "properties": {
    "activities": [
      {
        "name": "CopyBlobsToUAE",
        "type": "Copy",
        "inputs": [
          {
            "referenceName": "SourceBlobUKSouth",
            "type": "DatasetReference"
          }
        ],
        "outputs": [
          {
            "referenceName": "DestBlobUAENorth",
            "type": "DatasetReference"
          }
        ],
        "typeProperties": {
          "source": {
            "type": "BlobSource",
            "recursive": true
          },
          "sink": {
            "type": "BlobSink"
          }
        }
      }
    ],
    "triggers": [
      {
        "name": "HourlySync",
        "type": "ScheduleTrigger",
        "typeProperties": {
          "recurrence": {
            "frequency": "Hour",
            "interval": 1
          }
        }
      }
    ]
  }
}
```

**Checklist:**
- [ ] Identify all storage accounts requiring replication
- [ ] Choose replication method based on RPO requirements
- [ ] Set up automated sync (AzCopy script, ADF, or Logic App)
- [ ] Test data integrity after replication
- [ ] Monitor replication lag and failures
- [ ] Document failover procedure for storage accounts

#### Task 2.2: Azure SQL Database Geo-Replication
```bash
# Enable active geo-replication to UAE North
az sql db replica create \
  --resource-group rg-uksouth-prod \
  --server sql-uksouth-prod \
  --name db-app-prod \
  --partner-resource-group rg-dr-uaenorth-prod \
  --partner-server sql-uaenorth-dr \
  --secondary-type Geo

# Verify replication status
az sql db replica list-links \
  --resource-group rg-uksouth-prod \
  --server sql-uksouth-prod \
  --name db-app-prod
```

**Checklist:**
- [ ] Create SQL Server in UAE North with same admin credentials
- [ ] Configure firewall rules to allow cross-region replication
- [ ] Enable active geo-replication for each database
- [ ] Monitor replication lag (should be < 5 seconds typically)
- [ ] Test planned failover (non-disruptive)
- [ ] Document failover and failback procedures
- [ ] Set up alerts for replication lag > threshold

#### Task 2.3: Cosmos DB Multi-Region Setup
```bash
# Add UAE North as read region
az cosmosdb update \
  --resource-group rg-uksouth-prod \
  --name cosmos-app-prod \
  --locations regionName=uksouth failoverPriority=0 isZoneRedundant=true \
  --locations regionName=uaenorth failoverPriority=1 isZoneRedundant=true

# Enable multi-region writes (if needed)
az cosmosdb update \
  --resource-group rg-uksouth-prod \
  --name cosmos-app-prod \
  --enable-multiple-write-locations true
```

**Checklist:**
- [ ] Add UAE North as secondary region
- [ ] Choose consistency level (Strong not recommended for cross-geography)
- [ ] Decide on single-write vs. multi-write regions
- [ ] Update application connection strings to use multi-region endpoint
- [ ] Test automatic failover
- [ ] Monitor RU consumption in both regions
- [ ] Set up conflict resolution policy if using multi-write

#### Task 2.4: Azure Database for MySQL/PostgreSQL
```bash
# Create read replica in UAE North
az mysql flexible-server replica create \
  --resource-group rg-dr-uaenorth-prod \
  --name mysql-uaenorth-dr \
  --source-server /subscriptions/{sub-id}/resourceGroups/rg-uksouth-prod/providers/Microsoft.DBforMySQL/flexibleServers/mysql-uksouth-prod
```

**Checklist:**
- [ ] Create read replica in UAE North
- [ ] Monitor replication lag
- [ ] Test promotion of replica to standalone server
- [ ] Update application connection strings for read/write split
- [ ] Document failover procedure
- [ ] Set up alerts for replication failures

---

### Phase 3: Compute & Application Deployment (Week 2-3)

#### Task 3.1: Azure Site Recovery (ASR) for VMs
```bash
# Create Recovery Services Vault
az backup vault create \
  --resource-group rg-dr-uaenorth-prod \
  --name rsv-dr-uaenorth \
  --location uaenorth

# Enable replication for VM (via Portal or PowerShell)
# Note: Azure CLI doesn't fully support ASR configuration
# Use Azure Portal or PowerShell for ASR setup
```

**PowerShell for ASR:**
```powershell
# Set up ASR replication policy
$ReplicationPolicy = New-AzRecoveryServicesAsrPolicy `
  -Name "ReplicationPolicy" `
  -ReplicationProvider "A2A" `
  -RecoveryPointRetentionInHours 24 `
  -ApplicationConsistentSnapshotFrequencyInHours 4

# Enable replication for VM
$VM = Get-AzVM -ResourceGroupName "rg-uksouth-prod" -Name "vm-app-01"
New-AzRecoveryServicesAsrReplicationProtectedItem `
  -AzureToAzure `
  -AzureVmId $VM.Id `
  -RecoveryResourceGroupId "/subscriptions/{sub-id}/resourceGroups/rg-dr-uaenorth-prod" `
  -RecoveryAzureNetworkId "/subscriptions/{sub-id}/resourceGroups/rg-dr-uaenorth-prod/providers/Microsoft.Network/virtualNetworks/vnet-dr-uaenorth" `
  -RecoveryAzureSubnetName "subnet-app"
```

**Checklist:**
- [ ] Create Recovery Services Vault in UAE North
- [ ] Configure replication policy (RPO, retention)
- [ ] Enable replication for all critical VMs
- [ ] Map UK South VNet/subnets to UAE North equivalents
- [ ] Configure compute settings (VM size, availability set)
- [ ] Test failover for each VM
- [ ] Document failover runbook
- [ ] Set up ASR monitoring and alerts

#### Task 3.2: AKS Cluster Setup in UAE North
```bash
# Create AKS cluster in UAE North
az aks create \
  --resource-group rg-dr-uaenorth-prod \
  --name aks-dr-uaenorth \
  --location uaenorth \
  --node-count 3 \
  --node-vm-size Standard_D4s_v3 \
  --network-plugin azure \
  --vnet-subnet-id /subscriptions/{sub-id}/resourceGroups/rg-dr-uaenorth-prod/providers/Microsoft.Network/virtualNetworks/vnet-dr-uaenorth/subnets/subnet-aks \
  --enable-managed-identity \
  --attach-acr /subscriptions/{sub-id}/resourceGroups/rg-shared/providers/Microsoft.ContainerRegistry/registries/acrshared \
  --zones 1 2 3

# Get credentials
az aks get-credentials \
  --resource-group rg-dr-uaenorth-prod \
  --name aks-dr-uaenorth \
  --context aks-dr-uaenorth
```

**Checklist:**
- [ ] Match AKS version with UK South cluster
- [ ] Use same node VM sizes (verify availability in UAE North)
- [ ] Configure same network plugin (Azure CNI or Kubenet)
- [ ] Attach to shared Azure Container Registry
- [ ] Set up Azure AD integration (if used)
- [ ] Deploy cluster-level resources (ingress controller, cert-manager, monitoring)
- [ ] Configure GitOps (ArgoCD/Flux) to deploy applications
- [ ] Test application deployment and functionality

#### Task 3.3: App Service Deployment
```bash
# Create App Service Plan in UAE North
az appservice plan create \
  --resource-group rg-dr-uaenorth-prod \
  --name asp-dr-uaenorth \
  --location uaenorth \
  --sku P1V2 \
  --is-linux

# Create Web App
az webapp create \
  --resource-group rg-dr-uaenorth-prod \
  --plan asp-dr-uaenorth \
  --name app-dr-uaenorth \
  --runtime "DOTNETCORE:8.0"

# Configure deployment from ACR or GitHub
az webapp config container set \
  --resource-group rg-dr-uaenorth-prod \
  --name app-dr-uaenorth \
  --docker-custom-image-name acrshared.azurecr.io/app:latest \
  --docker-registry-server-url https://acrshared.azurecr.io
```

**Checklist:**
- [ ] Create App Service Plan with same SKU as UK South
- [ ] Deploy web apps with same configuration
- [ ] Configure application settings and connection strings
- [ ] Set up deployment slots (if used)
- [ ] Configure custom domains and SSL certificates
- [ ] Test application functionality
- [ ] Set up Traffic Manager for automatic failover

---

### Phase 4: Messaging & Event Services (Week 3)

#### Task 4.1: Service Bus Geo-Disaster Recovery
```bash
# Create Service Bus namespace in UAE North
az servicebus namespace create \
  --resource-group rg-dr-uaenorth-prod \
  --name sb-dr-uaenorth \
  --location uaenorth \
  --sku Premium

# Set up Geo-DR pairing (Premium tier only)
az servicebus georecovery-alias set \
  --resource-group rg-uksouth-prod \
  --namespace-name sb-uksouth-prod \
  --alias sb-app-dr \
  --partner-namespace /subscriptions/{sub-id}/resourceGroups/rg-dr-uaenorth-prod/providers/Microsoft.ServiceBus/namespaces/sb-dr-uaenorth
```

**Checklist:**
- [ ] Upgrade to Premium tier if not already (required for Geo-DR)
- [ ] Create Service Bus namespace in UAE North
- [ ] Configure Geo-DR pairing
- [ ] Update application connection strings to use alias
- [ ] Recreate queues/topics in UAE North (metadata only, messages replicate)
- [ ] Test failover and failback
- [ ] Document failover procedure

#### Task 4.2: Event Hubs Geo-Disaster Recovery
```bash
# Create Event Hubs namespace in UAE North
az eventhubs namespace create \
  --resource-group rg-dr-uaenorth-prod \
  --name eh-dr-uaenorth \
  --location uaenorth \
  --sku Standard

# Set up Geo-DR pairing
az eventhubs georecovery-alias set \
  --resource-group rg-uksouth-prod \
  --namespace-name eh-uksouth-prod \
  --alias eh-app-dr \
  --partner-namespace /subscriptions/{sub-id}/resourceGroups/rg-dr-uaenorth-prod/providers/Microsoft.EventHub/namespaces/eh-dr-uaenorth
```

**Checklist:**
- [ ] Create Event Hubs namespace in UAE North
- [ ] Configure Geo-DR pairing
- [ ] Recreate event hubs in UAE North
- [ ] Update producer/consumer connection strings to use alias
- [ ] Test failover
- [ ] Monitor replication lag

---

### Phase 5: Security & Identity (Week 3-4)

#### Task 5.1: Key Vault Replication
```bash
# Create Key Vault in UAE North
az keyvault create \
  --resource-group rg-dr-uaenorth-prod \
  --name kv-dr-uaenorth \
  --location uaenorth \
  --enable-soft-delete \
  --enable-purge-protection

# Copy secrets from UK South to UAE North (manual or scripted)
# Get all secrets from UK South
SECRETS=$(az keyvault secret list --vault-name kv-uksouth-prod --query "[].name" -o tsv)

# Copy each secret
for SECRET in $SECRETS; do
  VALUE=$(az keyvault secret show --vault-name kv-uksouth-prod --name $SECRET --query "value" -o tsv)
  az keyvault secret set --vault-name kv-dr-uaenorth --name $SECRET --value "$VALUE"
done
```

**Checklist:**
- [ ] Create Key Vault in UAE North with same configuration
- [ ] Copy all secrets, keys, and certificates
- [ ] Configure access policies or RBAC
- [ ] Enable Managed Identity access for applications
- [ ] Set up automated secret sync (Azure Automation or Logic App)
- [ ] Test application access to UAE North Key Vault
- [ ] Document secret rotation procedures

#### Task 5.2: Managed Identity Configuration
```bash
# Assign Managed Identity to UAE North resources
az vm identity assign \
  --resource-group rg-dr-uaenorth-prod \
  --name vm-app-dr-01

# Grant Key Vault access
az keyvault set-policy \
  --name kv-dr-uaenorth \
  --object-id <managed-identity-object-id> \
  --secret-permissions get list
```

**Checklist:**
- [ ] Enable Managed Identity on all UAE North resources
- [ ] Grant necessary RBAC roles
- [ ] Update Key Vault access policies
- [ ] Test Managed Identity authentication
- [ ] Document identity mappings

---

### Phase 6: Monitoring & Alerting (Week 4)

#### Task 6.1: Log Analytics Workspace
```bash
# Create Log Analytics workspace in UAE North
az monitor log-analytics workspace create \
  --resource-group rg-dr-uaenorth-prod \
  --workspace-name law-dr-uaenorth \
  --location uaenorth

# Configure diagnostic settings for resources
az monitor diagnostic-settings create \
  --resource /subscriptions/{sub-id}/resourceGroups/rg-dr-uaenorth-prod/providers/Microsoft.Compute/virtualMachines/vm-app-dr-01 \
  --name diag-vm-app-dr-01 \
  --workspace /subscriptions/{sub-id}/resourceGroups/rg-dr-uaenorth-prod/providers/Microsoft.OperationalInsights/workspaces/law-dr-uaenorth \
  --logs '[{"category": "Administrative", "enabled": true}]' \
  --metrics '[{"category": "AllMetrics", "enabled": true}]'
```

**Checklist:**
- [ ] Create Log Analytics workspace in UAE North
- [ ] Configure diagnostic settings for all resources
- [ ] Replicate custom queries and workbooks
- [ ] Set up cross-region monitoring dashboard
- [ ] Configure alerts for replication lag
- [ ] Test alert notifications

#### Task 6.2: Application Insights
```bash
# Create Application Insights in UAE North
az monitor app-insights component create \
  --resource-group rg-dr-uaenorth-prod \
  --app appi-dr-uaenorth \
  --location uaenorth \
  --workspace /subscriptions/{sub-id}/resourceGroups/rg-dr-uaenorth-prod/providers/Microsoft.OperationalInsights/workspaces/law-dr-uaenorth
```

**Checklist:**
- [ ] Create Application Insights instance
- [ ] Update application instrumentation keys
- [ ] Configure availability tests from multiple regions
- [ ] Set up custom metrics and events
- [ ] Create alerts for application errors

---

### Phase 7: Failover Testing & Validation (Week 5-6)

#### Task 7.1: Planned Failover Test
```bash
# Test SQL Database failover
az sql db replica set-primary \
  --resource-group rg-dr-uaenorth-prod \
  --server sql-uaenorth-dr \
  --name db-app-prod

# Test Traffic Manager failover
az network traffic-manager endpoint update \
  --resource-group rg-global \
  --profile-name tm-app-global \
  --name endpoint-uksouth \
  --type azureEndpoints \
  --endpoint-status Disabled
```

**Failover Test Checklist:**
- [ ] Schedule maintenance window
- [ ] Notify stakeholders
- [ ] Execute failover for each service:
  - [ ] Traffic Manager (disable UK South endpoint)
  - [ ] Azure SQL Database (planned failover)
  - [ ] Cosmos DB (manual failover)
  - [ ] Service Bus (break Geo-DR pairing)
  - [ ] Event Hubs (break Geo-DR pairing)
  - [ ] ASR VMs (test failover)
- [ ] Validate application functionality in UAE North
- [ ] Measure actual RTO achieved
- [ ] Test failback to UK South
- [ ] Document issues and lessons learned

#### Task 7.2: Data Consistency Validation
```sql
-- Compare record counts between UK South and UAE North
-- UK South
SELECT COUNT(*) FROM Orders;

-- UAE North (after failover)
SELECT COUNT(*) FROM Orders;

-- Check for data discrepancies
SELECT * FROM Orders 
WHERE LastModified > DATEADD(minute, -5, GETUTCDATE())
ORDER BY LastModified DESC;
```

**Checklist:**
- [ ] Verify database record counts match
- [ ] Check for missing or duplicate records
- [ ] Validate blob storage file counts
- [ ] Test application read/write operations
- [ ] Verify message queue processing
- [ ] Document any data loss (measure actual RPO)

---

## Critical Configuration Items

### Connection Strings & Endpoints

**UK South (Primary):**
```ini
# SQL Database
SQL_CONNECTION_STRING=Server=tcp:sql-uksouth-prod.database.windows.net,1433;Database=db-app-prod;

# Storage Account
STORAGE_CONNECTION_STRING=DefaultEndpointsProtocol=https;AccountName=stuksouthprod;AccountKey=...;EndpointSuffix=core.windows.net

# Service Bus
SERVICE_BUS_CONNECTION_STRING=Endpoint=sb://sb-uksouth-prod.servicebus.windows.net/;SharedAccessKeyName=...

# Cosmos DB
COSMOS_DB_ENDPOINT=https://cosmos-app-prod.documents.azure.com:443/

# Key Vault
KEY_VAULT_URI=https://kv-uksouth-prod.vault.azure.net/
```

**UAE North (DR):**
```ini
# SQL Database (use Geo-DR listener)
SQL_CONNECTION_STRING=Server=tcp:sql-uaenorth-dr.database.windows.net,1433;Database=db-app-prod;

# Storage Account
STORAGE_CONNECTION_STRING=DefaultEndpointsProtocol=https;AccountName=stuaenorthdr;AccountKey=...;EndpointSuffix=core.windows.net

# Service Bus (use Geo-DR alias)
SERVICE_BUS_CONNECTION_STRING=Endpoint=sb://sb-app-dr.servicebus.windows.net/;SharedAccessKeyName=...

# Cosmos DB (multi-region endpoint)
COSMOS_DB_ENDPOINT=https://cosmos-app-prod.documents.azure.com:443/

# Key Vault
KEY_VAULT_URI=https://kv-dr-uaenorth.vault.azure.net/
```

### Region-Aware Application Configuration

**Option 1: Environment Variables**
```bash
export AZURE_REGION=uksouth
export PRIMARY_REGION=uksouth
export DR_REGION=uaenorth
export FAILOVER_MODE=false
```

**Option 2: Azure App Configuration**
```bash
# Create App Configuration in both regions
az appconfig create \
  --resource-group rg-uksouth-prod \
  --name appconfig-uksouth \
  --location uksouth

# Set region-specific configuration
az appconfig kv set \
  --name appconfig-uksouth \
  --key "Region" \
  --value "uksouth"

az appconfig kv set \
  --name appconfig-uksouth \
  --key "DatabaseEndpoint" \
  --value "sql-uksouth-prod.database.windows.net"
```

---

## Automation Scripts

### Failover Automation Script
```bash
#!/bin/bash
# failover-to-uae.sh - Automated failover to UAE North

set -e

echo "Starting failover to UAE North..."

# 1. Disable UK South Traffic Manager endpoint
echo "Disabling UK South endpoint..."
az network traffic-manager endpoint update \
  --resource-group rg-global \
  --profile-name tm-app-global \
  --name endpoint-uksouth \
  --endpoint-status Disabled

# 2. Failover SQL Database
echo "Failing over SQL Database..."
az sql db replica set-primary \
  --resource-group rg-dr-uaenorth-prod \
  --server sql-uaenorth-dr \
  --name db-app-prod

# 3. Break Service Bus Geo-DR pairing
echo "Breaking Service Bus Geo-DR..."
az servicebus georecovery-alias break-pair \
  --resource-group rg-uksouth-prod \
  --namespace-name sb-uksouth-prod \
  --alias sb-app-dr

# 4. Failover Cosmos DB
echo "Failing over Cosmos DB..."
az cosmosdb failover-priority-change \
  --resource-group rg-uksouth-prod \
  --name cosmos-app-prod \
  --failover-policies uaenorth=0 uksouth=1

# 5. Trigger ASR failover (manual step - requires confirmation)
echo "ASR failover must be triggered manually via Azure Portal"
echo "Navigate to Recovery Services Vault > Replicated Items > Failover"

echo "Failover to UAE North completed!"
echo "Verify application functionality at: https://app-contoso-global.trafficmanager.net"
```

### Health Check Script
```bash
#!/bin/bash
# health-check.sh - Verify DR readiness

echo "Checking DR readiness..."

# Check VNet peering status
PEERING_STATUS=$(az network vnet peering show \
  --resource-group rg-uksouth-prod \
  --name peer-uksouth-to-uaenorth \
  --vnet-name vnet-uksouth \
  --query "peeringState" -o tsv)

echo "VNet Peering Status: $PEERING_STATUS"

# Check SQL replication lag
REPLICATION_LAG=$(az sql db replica list-links \
  --resource-group rg-uksouth-prod \
  --server sql-uksouth-prod \
  --name db-app-prod \
  --query "[0].replicationState" -o tsv)

echo "SQL Replication State: $REPLICATION_LAG"

# Check Cosmos DB regions
COSMOS_REGIONS=$(az cosmosdb show \
  --resource-group rg-uksouth-prod \
  --name cosmos-app-prod \
  --query "locations[].locationName" -o tsv)

echo "Cosmos DB Regions: $COSMOS_REGIONS"

# Check ASR replication health
echo "Check ASR health in Azure Portal: Recovery Services Vault > Replicated Items"

echo "Health check completed!"
```

---

## Performance Considerations

### Latency Impact Matrix

| Service | Synchronous? | Latency Sensitivity | UAE North Impact | Mitigation |
|---------|-------------|-------------------|-----------------|------------|
| **Azure SQL Active Geo-Replication** | Async | Low | ✅ Acceptable | Asynchronous replication |
| **Cosmos DB Multi-Region** | Async (Eventual) | Medium | ✅ Acceptable | Use Eventual/Session consistency |
| **Service Bus Geo-DR** | Async | Low | ✅ Acceptable | Metadata replication only |
| **Storage Replication** | Async | Low | ✅ Acceptable | Scheduled sync |
| **ASR VM Replication** | Async | Low | ✅ Acceptable | Continuous async replication |
| **Real-time APIs** | Sync | High | ❌ Not viable | Keep in UK South/UK West |
| **Azure OpenAI** | Sync | High | ❌ Not available | NOT available in UAE North |

### RPO/RTO Targets

| Service | Expected RPO | Expected RTO | Notes |
|---------|-------------|-------------|-------|
| **Azure SQL Database** | < 5 seconds | < 30 minutes | Active geo-replication |
| **Cosmos DB** | < 15 seconds | < 5 minutes | Automatic failover |
| **Service Bus** | < 1 minute | < 5 minutes | Metadata only |
| **Event Hubs** | < 1 minute | < 5 minutes | Metadata only |
| **ASR VMs** | ~5 minutes | ~1 hour | Depends on VM count |
| **Storage (AzCopy sync)** | 1-24 hours | < 1 hour | Depends on sync frequency |

---

## Troubleshooting Guide

### Common Issues

**Issue 1: VNet Peering Not Working**
```bash
# Check peering status
az network vnet peering show \
  --resource-group rg-uksouth-prod \
  --name peer-uksouth-to-uaenorth \
  --vnet-name vnet-uksouth

# Verify NSG rules allow traffic
az network nsg rule list \
  --resource-group rg-uksouth-prod \
  --nsg-name nsg-app \
  --output table

# Test connectivity
az vm run-command invoke \
  --resource-group rg-uksouth-prod \
  --name vm-test-uksouth \
  --command-id RunShellScript \
  --scripts "ping -c 4 10.1.1.4"
```

**Issue 2: SQL Replication Lag High**
```sql
-- Check replication lag
SELECT 
    partner_server,
    partner_database,
    replication_state_desc,
    replication_lag_sec
FROM sys.dm_geo_replication_link_status;

-- If lag > 60 seconds, check:
-- 1. Network connectivity
-- 2. Primary database load
-- 3. Secondary region capacity
```

**Issue 3: ASR Replication Failing**
```bash
# Check ASR replication health via PowerShell
Get-AzRecoveryServicesAsrReplicationProtectedItem \
  -ProtectionContainer $container \
  | Select-Object Name, ReplicationHealth, ReplicationHealthErrors
```

---

## Post-Failover Validation Checklist

- [ ] **Traffic Manager**: Verify UAE North endpoint is receiving traffic
- [ ] **DNS Resolution**: Test DNS resolution from client locations
- [ ] **Database Connectivity**: Verify application can read/write to UAE North database
- [ ] **Storage Access**: Test blob/file storage read/write operations
- [ ] **Message Queues**: Verify Service Bus/Event Hubs message processing
- [ ] **Application Functionality**: Test critical user workflows
- [ ] **Performance**: Measure response times and compare to baseline
- [ ] **Monitoring**: Verify logs and metrics flowing to Log Analytics
- [ ] **Alerts**: Confirm alert rules are active and firing correctly
- [ ] **Security**: Verify authentication and authorization working
- [ ] **Data Integrity**: Run data consistency checks
- [ ] **Backup**: Verify backup jobs running in UAE North

---

## Compliance & Documentation

### Required Documentation

1. **Network Diagrams**
   - UK South architecture
   - UAE North architecture
   - Cross-region connectivity

2. **Data Flow Diagrams**
   - Replication flows
   - Failover sequences
   - Failback procedures

3. **Runbooks**
   - Failover procedure (step-by-step)
   - Failback procedure
   - Rollback procedure

4. **Configuration Management**
   - Infrastructure as Code (Terraform/Bicep)
   - Application configuration
   - Secret management

5. **Compliance Documentation**
   - Transfer Risk Assessment (TRA)
   - UK IDTA or SCCs
   - Data classification matrix
   - Audit logs

---

## Next Steps

1. **Answer all pre-implementation questions** in this document
2. **Verify service availability** in UAE North for your specific services
3. **Submit UAE North region access request** to Microsoft
4. **Design network architecture** with non-overlapping CIDRs
5. **Create detailed project plan** with timelines and resource allocation
6. **Begin Phase 1: Network Foundation** once access is approved
7. **Test each phase** before proceeding to the next
8. **Document everything** as you go

---

*Last Updated: February 10, 2026*  
*Document Owner: Platform Engineering Team*
