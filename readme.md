# SecureCryptoX

SecureCryptoX is a secure cryptocurrency wallet management system developed using **Flask** and **Microsoft SQL Server**. The application has been migrated to **Amazon Web Services (AWS)** with additional cloud security controls to improve security, availability, and monitoring.

## Features
- User Registration & Login
- Deposit & Withdraw Money
- Buy & Sell Bitcoin
- Transfer Bitcoin Between Users
- Wallet Management
- Transaction History
- Admin Dashboard
- Manager Dashboard

## Database Security Features
- Password Hashing
- Role-Based Access Control (RBAC)
- Row-Level Security (RLS)
- Dynamic Data Masking (DDM)
- AES-256 Encryption
- SQL Server Audit Logging
- Suspicious Activity Monitoring
- CSRF Protection
- SQL Injection Prevention

## AWS Cloud Security
- Amazon EC2
- Amazon RDS (SQL Server)
- Amazon VPC
- Application Load Balancer (ALB)
- AWS WAF
- Security Groups
- IAM Roles
- AWS CloudTrail
- Database Encryption
- Infrastructure as Code (Terraform)

## Security Validation
- Nmap Port Scanning
- AWS WAF Protection Testing
- CloudTrail Activity Verification
- Database Encryption Verification

## Technologies Used
- Python Flask
- Microsoft SQL Server
- PyODBC
- HTML
- CSS
- JavaScript
- Amazon Web Services (AWS)
- Terraform
- Nmap

## Run Project

Clone the repository:

```bash
git clone <repository-url>
cd SecureCryptoX
```

Install the required packages:

```bash
pip install -r requirements.txt
```

Run the application:

```bash
python app.py
```

## User Roles

- **Admin** – Full system access
- **Manager** – Monitor suspicious activities and audit logs
- **User** – Manage wallet and cryptocurrency transactions

## Project Overview

The project demonstrates the secure migration of a traditional web application to AWS by implementing cloud security best practices, including secure networking, access control, monitoring, encryption, and infrastructure automation.

## Authors

- **1211111953** – Mohamed Shahrizal bin Samsudeen
- **1211111537** – Vishal Nair A/L Raman
- **241UC240R7** – Chia Chee Yong
