# Building Actionable AI: Automating IT Requests with Agent Builder and One Workflow

This directory contains resources and workflows for building an AI agent capable of automating laptop refresh requests for Elastic employees. It accompanies the blog post "Building Actionable AI: Automating IT Requests with Agent Builder and One Workflow".

## Contents

### Files

- **laptop_refresh_agent_instructions.ipynb**: A Jupyter Notebook containing the detailed system instructions and operating protocol for the Laptop Refresh Agent. It outlines the agent's mission, steps for user verification, eligibility checks, device selection, and request submission logic.

### Directories

#### Laptop Refresh Workflows

Contains specific YAML workflow definitions used by the Laptop Refresh Agent:

- `CasePointServiceNow.yaml`: Workflow definitions for ServiceNow interactions.
- `GetCurrentUsersData.yaml`: Workflow to retrieve current user details and asset data.
- `SubmitLaptopRefreshRequest.yaml`: Workflow to submit the final laptop refresh request to ServiceNow.

#### Try it yourself workflows

Contains generic ServiceNow workflow templates that can be used as a reference or starting point for your own automations:

- `Generic_ServiceNow_Catalog_Order.yaml`: Template for ordering items from a ServiceNow catalog.
- `Generic_ServiceNow_Create_Record.yaml`: Template for creating new records in ServiceNow.
- `Generic_ServiceNow_Get_Records.yaml`: Template for retrieving records from ServiceNow.
- `Generic_ServiceNow_Update_Record.yaml`: Template for updating existing ServiceNow records.
