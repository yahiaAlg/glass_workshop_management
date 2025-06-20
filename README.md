# Django Glass Shop Management & Invoice System - AI Generation Prompt

## Project Overview

Create a simplified glass shop management and invoice system using Django framework for a glass retail business with the following technology stack:

- **Backend**: Django 4.x with Python 3.x
- **Frontend**: HTML5, CSS3, JavaScript ES6+
- **UI Framework**: Bootstrap 5
- **Icons**: Font Awesome 6
- **Charts**: Chart.js
- **Database**: sqlite

## System Requirements for Glass Shop

### 1. Company Profile Management

For glass retail shop business:

```python
# Company model structure
- Company name
- Business type (Glass retail & installation services)
- Shop address (multi-line support)
- Phone, Fax, Email, Website
- Legal identifiers (RC, ART, NIS, NIF, RIB) - this part is optional
- Capital social
- Logo upload capability
- Tax settings and rates
- Shop operating hours
- Basic certifications
```

### 2. Customer Management System

For glass shop clients:

```python
# Customer model structure
- Customer name/company
- Customer type (Individual/Commercial)
- Address (delivery/installation location)
- Phone, Email
- Legal identifiers (NIS, RC, ART) - for commercial clients (optional)
- Contact person (for companies)
- Payment terms
- Customer notes
- Customer status (Active/Inactive)
- Purchase history
```

### 3. Glass Products Inventory Management

Simple glass inventory system:

```python
# Glass Product model structure
- Product code (auto-generated)
- Product name/description
- Glass type (Window Glass, Mirror, Shower Glass, Table Top, etc.)
- Thickness (3mm, 4mm, 5mm, 6mm, 8mm, 10mm, 12mm, etc.)
- Standard sizes available
- Color/Tint (Clear, Bronze, Grey, Green, Blue, etc.)
- Surface finish (Polished, Frosted, Textured, etc.)
- Unit of measure (Square meter, Piece)
- Cost price per unit
- Selling price per unit
- Stock quantity
- Minimum stock level
- Supplier information
- Product category
- Product status (Active/Inactive)
- Product image
```

### 4. Simple Order Management

Basic order processing:

```python
# Order model structure
- Order number (auto-generated)
- Customer information
- Order date
- Delivery date (if applicable)
- Order status (Pending, Confirmed, Delivered, Cancelled)
- Order items with:
  - Glass product
  - Quantity
  - Unit price
  - Subtotal
- Delivery address (if different from customer address)
- Installation required (Yes/No)
- Order notes
- Total amount
```

### 5. Invoice Management System

Simplified glass shop invoice format:

#### Invoice Header
- Invoice number generation (GLS-YYYY-NNNN format)
- Invoice date and due date
- Order reference number (if applicable)
- Payment method (CASH, CARD, CHEQUE, TRANSFER)
- Customer information
- Delivery address (if applicable)

#### Invoice Body - Glass Items
Line items with:
- Item description
- Glass type and specifications (width, height, thickness, etc.)
- Quantity
- Unit of measure
- Unit price
- Line total

#### Additional Services
- Delivery charges
- Installation service
- Cutting service
- Packaging charges

#### Invoice Footer Calculations
- SUBTOTAL (Product costs)
- SERVICES TOTAL (Additional services)
- TOTAL (Total)
- DISCOUNT (if applicable)
- FINAL TOTAL

#### Additional Information
- Delivery date (if applicable)
- Installation notes
- Warranty information
- Payment terms

### 6. Supplier Management

Simple supplier tracking:

```python
# Supplier model structure
- Supplier name/company
- Contact person
- Phone, Email, Address
- Glass products supplied
- Payment terms
- Supplier notes
- Supplier status (Active/Inactive)
- Last order date
```

### 7. Authentication & User Management

Simplified user roles:

```python
# User roles (only 2 roles)
- Admin (full system access)
  - Manage all data
  - View all reports
  - System configuration
  - User management
  
- Worker (limited access)
  - Create/edit invoices
  - View customer information
  - Check inventory
  - Process orders
  - Cannot delete records
  - Cannot access financial reports
```

### 8. Dashboard with Integrated Reports

Single dashboard with all analytics:

#### Key Metrics Cards
- Today's sales
- This month's revenue
- Total customers
- Low stock alerts
- Pending orders
- Outstanding invoices

#### Charts & Visualizations (Embedded in Dashboard)
- Daily/weekly sales trends (line chart)
- Top selling glass products (bar chart)
- Customer type distribution (pie chart)
- Monthly revenue comparison
- Payment method statistics
- Inventory status overview

#### Quick Reports Section (Within Dashboard)
- Recent sales summary
- Top customers this month
- Low stock items list
- Overdue invoices
- Best selling products
- Today's orders summary

### 9. Payment Tracking

Simple payment management:

```python
# Payment model structure
- Payment reference
- Invoice reference
- Payment date
- Amount paid
- Payment method
- Payment status (Completed, Pending, Failed)
- Payment notes
```

## Technical Implementation Details

### Simplified Django Project Structure

```
.
└── project/
    ├── apps/
    │   ├── authentication/
    │   │   ├── admin.py
    │   │   ├── apps.py
    │   │   ├── forms.py
    │   │   ├── migrations/
    │   │   │   └── 0001_initial.py
    │   │   ├── models.py
    │   │   ├── urls.py
    │   │   └── views.py
    │   ├── company/
    │   │   ├── admin.py
    │   │   ├── apps.py
    │   │   ├── forms.py
    │   │   ├── migrations/
    │   │   │   └── 0001_initial.py
    │   │   ├── models.py
    │   │   ├── urls.py
    │   │   └── views.py
    │   ├── customers/
    │   │   ├── admin.py
    │   │   ├── apps.py
    │   │   ├── forms.py
    │   │   ├── migrations/
    │   │   │   └── 0001_initial.py
    │   │   ├── models.py
    │   │   ├── urls.py
    │   │   └── views.py
    │   ├── dashboard/
    │   │   ├── admin.py
    │   │   ├── apps.py
    │   │   ├── management/
    │   │   │   └── commands/
    │   │   │       └── populate_sample_data.py
    │   │   ├── urls.py
    │   │   └── views.py
    │   ├── inventory/
    │   │   ├── admin.py
    │   │   ├── apps.py
    │   │   ├── forms.py
    │   │   ├── migrations/
    │   │   │   └── 0001_initial.py
    │   │   ├── models.py
    │   │   ├── urls.py
    │   │   └── views.py
    │   ├── invoices/
    │   │   ├── admin.py
    │   │   ├── apps.py
    │   │   ├── forms.py
    │   │   ├── migrations/
    │   │   │   └── 0001_initial.py
    │   │   ├── models.py
    │   │   ├── urls.py
    │   │   └── views.py
    │   ├── orders/
    │   │   ├── admin.py
    │   │   ├── apps.py
    │   │   ├── forms.py
    │   │   ├── migrations/
    │   │   │   └── 0001_initial.py
    │   │   ├── models.py
    │   │   ├── urls.py
    │   │   └── views.py
    │   └── suppliers/
    │       ├── admin.py
    │       ├── apps.py
    │       ├── forms.py
    │       ├── migrations/
    │       │   └── 0001_initial.py
    │       ├── models.py
    │       ├── urls.py
    │       └── views.py
    ├── config/
    │   ├── settings.py
    │   ├── urls.py
    │   └── wsgi.py
    ├── db.sqlite3
    ├── manage.py
    ├── requirements.txt
    ├── static/
    │   ├── css/
    │   └── js/
    └── templates/
        ├── authentication/
        │   ├── create_user.html
        │   └── login.html
        ├── base.html
        ├── company/
        │   └── profile.html
        ├── customers/
        │   ├── delete.html
        │   ├── detail.html
        │   ├── form.html
        │   └── list.html
        ├── dashboard/
        │   ├── home.html
        │   └── reports.html
        ├── inventory/
        │   ├── delete.html
        │   ├── detail.html
        │   ├── form.html
        │   ├── list.html
        │   └── low_stock.html
        ├── invoices/
        │   ├── add_payment.html
        │   ├── delete.html
        │   ├── detail.html
        │   ├── form.html
        │   ├── list.html
        │   └── print.html
        ├── orders/
        │   ├── delete.html
        │   ├── detail.html
        │   ├── form.html
        │   └── list.html
        └── suppliers/
            ├── delete.html
            ├── detail.html
            ├── form.html
            └── list.html

```

### Bootstrap 5 UI Components for Glass Shop

- Clean navigation sidebar
- Responsive data tables for inventory
- Simple modal dialogs for CRUD operations
- Cards for dashboard metrics
- Form validation styling
- Print-friendly invoice templates
- Mobile-responsive design

### JavaScript Functionality

Glass shop specific features:
- Invoice line item calculations
- Real-time total updates
- Stock level warnings
- Auto-complete for product selection
- Print invoice functionality
- Simple chart interactions
- Form validation

### Database Models Priority

1. **Company**
2. **User** (Django's default user and profile model for additional informations )
3. **Customer**
4. **GlassProduct** (inventory)
5. **Order**
6. **OrderItem**
7. **Invoice**
8. **InvoiceItem**
9. **Supplier**
10. **Payment**

### Key Features to Implement

#### Inventory Management
- Simple stock tracking
- Low stock alerts
- Basic product catalog
- Supplier tracking

#### Sales Processing
- Quick order creation
- Invoice generation
- Payment recording
- Customer history

#### Basic Reporting
- Sales summaries
- Inventory reports
- Customer reports
- Financial overview

### Security Requirements

- Basic role-based access (Admin/Worker)
- Form validation and CSRF protection
- Secure file uploads
- Basic audit logging

### Localization Support

- French language support
- Local currency formatting
- Date formatting (DD/MM/YYYY)
- Tax compliance

## Sample Code Structure Request

Generate simplified Django application with:

1. **Models**: Essential database models only
2. **Views**: Basic CRUD operations
3. **Templates**: Clean Bootstrap 5 templates
4. **Forms**: Simple forms with validation
5. **JavaScript**: Basic calculations and interactions
6. **CSS**: Clean styling for glass shop theme
7. **URLs**: Simple URL patterns
8. **Settings**: Basic configuration
9. **Requirements**: Essential dependencies only

## Glass Shop Specific Features

#### Product Catalog
- Glass type categorization
- Size and thickness options
- Price management
- Stock tracking

#### Quick Invoice Creation
- Fast product selection
- Automatic calculations
- Print functionality
- Payment recording

#### Customer Management
- Contact information
- Purchase history
- Payment tracking
- Notes and preferences

#### Simple Inventory
- Stock levels
- Reorder alerts
- Supplier information
- Basic reporting

## Performance Requirements

- Fast invoice creation (<2 seconds)
- Quick product search
- Efficient dashboard loading
- Simple and intuitive interface

## Business Logic Considerations

### Pricing Management
- Simple markup calculations
- Discount applications
- Service charges
- Tax calculations

### Inventory Control
- Stock level monitoring
- Simple reorder alerts
- Basic supplier management
- Purchase tracking

### Customer Service
- Order history tracking
- Payment status monitoring
- Simple customer notes
- Contact management

This system provides essential glass shop management capabilities with professional invoicing, basic inventory control, and simple customer management while maintaining ease of use and efficient operations for a small to medium glass retail business.

NOTICE: Create the Django files and templates for this glass shop project as per the simplified requirements. Use only Django, HTML, CSS, and JavaScript - no TypeScript, React, or Vue.