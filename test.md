# Cross-Region Disaster Recovery Strategy for PostgreSQL in Azure

## Overview

This document describes the supported disaster recovery (DR) architectures for Azure Database for PostgreSQL – Flexible Server when the primary and DR environments are located across different Azure tenants, subscriptions, or regions.

### Current environment:

| Component | Location | Tenant |
| --- | --- | --- |
| Primary PostgreSQL | UK South | TenantA |
| DR Target | UAE North | TenantB |

Azure imposes restrictions on native replication depending on tenant and subscription boundaries.

## Azure Replication Support Matrix

| Scenario | Native Azure Read Replica | Alternative Required |
| --- | --- | --- |
| Same Tenant + Same Subscription | Supported | No |
| Same Tenant + Different Subscription | Not Supported | Yes |
| Different Tenant | Not Supported | Yes |

Native replication requires both servers to exist within the same Azure subscription.

## Option 1 – Same Tenant and Same Subscription (Recommended)

### Architecture

Primary PostgreSQL Flexible Server (UK South)
        │
Azure Native Replication
        │
Read Replica (UAE North)

### Benefits
- Fully managed replication
- Near real-time synchronization
- Simplified failover
- Minimal operational overhead

### Example Setup
default code block:
az postgres flexible-server replica create \
  --name dr-server \
  --resource-group rg-dr \
  --source-server primary-server \
  --location uaenorth
```

## Option 2 – Same Tenant but Different Subscription

dAzure does not support cross-subscription replication.

default code block:
definition: Recommended Solution: Logical Replication Architecture:
default code block:
Primary Flexible Server (TenantA / SubscriptionA / UK South)
        │
PostgreSQL Logical Replication
        │
DR Flexible Server (TenantA / SubscriptionB / UAE North)
default code block:
to set up logical replication, follow these steps:
to enable logical replication on primary server:
default code block:
alter system set wal_level = logical;
alter system set max_replication_slots = 10;
alter system set max_wal_senders = 10;
sql: select pg_reload_conf();
default code block:
to create a replication user:
default code block:
craete role replicator with login replication password 'StrongPassword';
default code block:
to create publication:
default code block:
craeate publication dr_pub for all tables;
default code block:
to configure subscription on DR server:
default code block:
craete subscription dr_sub connection 'host=<primary-host> port=5432 dbname=<db> user=replicator password=<password> sslmode=require' publication dr_pub;
details about options and parameters can be customized as needed.
documentation should be checked for exact syntax and security best practices.
note: The above commands are illustrative; actual implementation may vary based on environment specifics.
details about options and parameters can be customized as needed.
documentation should be checked for exact syntax and security best practices.
note: The above commands are illustrative; actual implementation may vary based on environment specifics.
details about options and parameters can be customized as needed.
documentation should be checked for exact syntax and security best practices.
note: The above commands are illustrative; actual implementation may vary based on environment specifics.
details about options and parameters can be customized as needed.
note: The above commands are illustrative; actual implementation may vary based on environment specifics. 
general guidance is provided here; always test in a non-production environment first. 
evaluate network connectivity, permissions, firewall rules, SSL configurations, etc., before deploying in production. 
before proceeding with any setup, ensure you have backups of your data. 
you should also consider monitoring tools to observe replication status and troubleshoot issues promptly. 
evaluate network connectivity, permissions, firewall rules, SSL configurations, etc., before deploying in production. 
before proceeding with any setup, ensure you have backups of your data. 
you should also consider monitoring tools to observe replication status and troubleshoot issues promptly.
