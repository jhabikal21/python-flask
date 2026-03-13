Cross-Region Disaster Recovery Strategy for PostgreSQL in Azure
Overview

This document describes the supported disaster recovery (DR) architectures for Azure Database for PostgreSQL – Flexible Server when the primary and DR environments are located across different Azure tenants, subscriptions, or regions.

Current environment:

Component	Location	Tenant
Primary PostgreSQL	UK South	TenantA
DR Target	UAE North	TenantB

Azure imposes restrictions on native replication depending on tenant and subscription boundaries.

Azure Replication Support Matrix
Scenario	Native Azure Read Replica	Alternative Required
Same Tenant + Same Subscription	Supported	No
Same Tenant + Different Subscription	Not Supported	Yes
Different Tenant	Not Supported	Yes

Native replication requires both servers to exist within the same Azure subscription.

Option 1 – Same Tenant and Same Subscription (Recommended)
Architecture
Primary PostgreSQL Flexible Server (UK South)
        │
Azure Native Replication
        │
Read Replica (UAE North)
Benefits

Fully managed replication

Near real-time synchronization

Simplified failover

Minimal operational overhead

Example Setup
az postgres flexible-server replica create \
  --name dr-server \
  --resource-group rg-dr \
  --source-server primary-server \
  --location uaenorth
Option 2 – Same Tenant but Different Subscription

Azure does not support cross-subscription replication.

Recommended Solution: Logical Replication

Architecture:

Primary Flexible Server
(TenantA / SubscriptionA / UK South)
        │
PostgreSQL Logical Replication
        │
DR Flexible Server
(TenantA / SubscriptionB / UAE North)
Steps
1. Enable Logical Replication

On primary server:

ALTER SYSTEM SET wal_level = logical;
ALTER SYSTEM SET max_replication_slots = 10;
ALTER SYSTEM SET max_wal_senders = 10;
SELECT pg_reload_conf();
2. Create Replication User
CREATE ROLE replicator WITH LOGIN REPLICATION PASSWORD 'StrongPassword';
3. Create Publication
CREATE PUBLICATION dr_pub FOR ALL TABLES;
4. Configure Subscription on DR Server
CREATE SUBSCRIPTION dr_sub
CONNECTION 'host=<primary-host> port=5432 dbname=<db> user=replicator password=<password> sslmode=require'
PUBLICATION dr_pub;
Option 3 – Cross-Tenant DR (Current Scenario)

Since the DR environment exists in a different tenant, native Azure replication is not possible.

Possible Solutions
1. PostgreSQL Logical Replication

Same setup as above.

Advantages:

Works across tenants

Near real-time replication

Fully PostgreSQL native

2. Azure Database Migration Service

Another option is Azure Database Migration Service.

Architecture:

Primary PostgreSQL
       │
Azure Database Migration Service
       │
DR PostgreSQL

Advantages:

Continuous sync

Managed service

Limitations:

Additional cost

Operational complexity

3. Backup and Restore DR

Architecture:

Primary Database
      │
Scheduled Backup
      │
Azure Storage
      │
Restore to DR Database

Limitations:

Higher recovery point objective (RPO)

Not real-time

Option 4 – Migration to VM-Based PostgreSQL (Alternative DR Architecture)

If Azure platform limitations prevent desired DR architecture, the database can be migrated from Azure Flexible Server to PostgreSQL hosted on Azure Virtual Machines.

This provides full control over replication configuration.

Possible compute platform: Azure Virtual Machines

Architecture
Primary PostgreSQL VM (UK South)
        │
Streaming Replication
        │
DR PostgreSQL VM (UAE North)

This approach removes Azure-managed service restrictions.

Steps to Migrate from Flexible Server to VM-Based PostgreSQL
Step 1 – Deploy PostgreSQL VM

Create a Linux VM in Azure and install PostgreSQL.

Example:

Ubuntu VM
Install PostgreSQL
Configure storage and networking
Step 2 – Configure PostgreSQL for Replication

Edit postgresql.conf:

wal_level = replica
max_wal_senders = 10
wal_keep_size = 1GB
hot_standby = on
Step 3 – Configure Access

Update pg_hba.conf:

host replication replicator <DR_VM_IP>/32 md5
Step 4 – Take Base Backup

From DR VM:

pg_basebackup -h <PrimaryVM> -D /var/lib/postgresql/data -U replicator -P -R
Step 5 – Start DR Replica

Start PostgreSQL service on DR VM.

Replication will begin automatically.

Advantages of VM-Based PostgreSQL
Benefit	Description
Full Control	Complete access to PostgreSQL configuration
Flexible Replication	Streaming or logical replication
Cross-Tenant Support	No Azure platform restrictions
Custom Backup Strategy	Full control of backup tools
Limitations
Limitation	Description
Operational Overhead	Requires patching and maintenance
High Availability	Must configure manually
Monitoring	Requires custom monitoring setup
Networking Requirements

For all cross-region or cross-tenant scenarios:

Ensure connectivity between primary and DR

Configure firewall rules

Enable SSL connections

Use private networking where possible

Options include:

VNet Peering

Private endpoints

Secure public access

Recommended Architecture

For simplicity and operational efficiency:

Same Tenant
Same Subscription
Primary Region + Secondary Region
Native Azure Replication

If tenant separation is required, the recommended DR approach is PostgreSQL logical replication.

If platform restrictions become limiting, migrating to VM-based PostgreSQL replication provides full flexibility at the cost of additional operational responsibility.
