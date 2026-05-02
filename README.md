# Vehicle Maintenance Scheduler

A system for optimizing vehicle maintenance scheduling using knapsack optimization and API integration.

## Overview

This project includes:
- Registration and authentication modules
- A logging middleware for centralized logging
- A vehicle maintenance scheduler that optimizes task allocation across depots

## Setup

### Prerequisites
- Python 3.7+
- `pip` package manager

### Installation

```bash
pip install requests
```

## Usage

### 1. Register
Register your credentials with the evaluation service:

```bash
python register.py
```

Output includes `ClientID` and `ClientSecret` for authentication.

### 2. Get Access Token
Retrieve an access token for API requests:

```bash
python auth.py
```

### 3. Run Scheduler
Execute the vehicle maintenance scheduler:

```bash
python vehicle_maintence_scheduler/scheduler.py
```

The scheduler fetches depot and vehicle data, solves the knapsack optimization problem, and displays the optimal task allocation for each depot.

### 4. Re-run the demos

Use the helper script to fetch a token, run both demos, and print the outputs in one go:

```powershell
.\run_demos.ps1
```

## Screenshot Artifacts

The repository includes PNG outputs for submission evidence:

- `vehicle_maintence_scheduler/scheduler_output.png`
- `notification_app_be/priority_inbox_output.png`

## Notification Backend

The `notification_app_be/` folder contains the Stage 6 Priority Inbox backend implementation used for the notification system design.

## Architecture

The project follows a 6-stage design progression covering API design, persistent storage, query optimization, performance improvements, asynchronous redesign, and priority inbox logic.

See `notification_system_design.md` for detailed design documentation.

## Project Structure

```
.
├── auth.py                           # Authentication helper
├── register.py                       # Registration script
├── logging_middleware/
│   └── logger.py                     # Centralized logging module
├── vehicle_maintence_scheduler/
│   └── scheduler.py                  # Main scheduler application
├── notification_app_be/
│   └── priority_inbox.py             # Stage 6 Priority Inbox backend
├── notification_system_design.md     # Design documentation
├── run_demos.ps1                     # Helper script to run both demos
└── README.md                         # This file
```

## Roll Number

RA2311003010093
