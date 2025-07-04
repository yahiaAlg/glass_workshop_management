```
project/
├── apps/
│   ├── audit/
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── forms.py
│   │   ├── management/
│   │   │   └── commands/
│   │   │       └── populate_categories.py
│   │   ├── migrations/
│   │   │   └── 0001_initial.py
│   │   ├── models.py
│   │   ├── resources.py
│   │   ├── urls.py
│   │   └── views.py
│   ├── authentication/
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── forms.py
│   │   ├── migrations/
│   │   │   └── 0001_initial.py
│   │   ├── models.py
│   │   ├── urls.py
│   │   └── views.py
│   ├── backup/
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── forms.py
│   │   ├── migrations/
│   │   │   └── 0001_initial.py
│   │   ├── models.py
│   │   ├── services.py
│   │   ├── urls.py
│   │   └── views.py
│   ├── company/
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── forms.py
│   │   ├── migrations/
│   │   │   └── 0001_initial.py
│   │   ├── models.py
│   │   ├── resources.py
│   │   ├── urls.py
│   │   └── views.py
│   ├── customers/
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── forms.py
│   │   ├── migrations/
│   │   │   └── 0001_initial.py
│   │   ├── models.py
│   │   ├── resources.py
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
│   │   ├── resources.py
│   │   ├── urls.py
│   │   └── views.py
│   ├── invoices/
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── forms.py
│   │   ├── migrations/
│   │   │   ├── 0001_initial.py
│   │   │   └── 0002_initial.py
│   │   ├── models.py
│   │   ├── resources.py
│   │   ├── urls.py
│   │   └── views.py
│   ├── orders/
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── forms.py
│   │   ├── migrations/
│   │   │   └── 0001_initial.py
│   │   ├── models.py
│   │   ├── resources.py
│   │   ├── urls.py
│   │   └── views.py
│   └── suppliers/
│       ├── admin.py
│       ├── apps.py
│       ├── forms.py
│       ├── migrations/
│       │   └── 0001_initial.py
│       ├── models.py
│       ├── resources.py
│       ├── urls.py
│       └── views.py
├── config/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── db.sqlite3
├── manage.py
├── media/
│   ├── audit/
│   │   └── expenses/
│   │       └── 4/
│   │           └── facture_sonalgaz.webp
│   └── backups/
│       └── exports/
├── requirements.txt
├── static/
│   ├── css/
│   └── js/
└── templates/
    ├── audit/
    │   ├── dashboard.html
    │   ├── expense_confirm_delete.html
    │   ├── expense_detail.html
    │   ├── expense_form.html
    │   ├── expense_list.html
    │   ├── revenue_confirm_delete.html
    │   ├── revenue_detail.html
    │   ├── revenue_form.html
    │   ├── revenue_list.html
    │   └── upload_document.html
    ├── authentication/
    │   ├── create_user.html
    │   └── login.html
    ├── backup/
    │   ├── dashboard.html
    │   ├── delete.html
    │   ├── detail.html
    │   ├── export.html
    │   ├── import.html
    │   └── list.html
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
    │   ├── reports/
    │   │   ├── customer_reports.html
    │   │   ├── financial_reports.html
    │   │   ├── inventory_reports.html
    │   │   └── sales_reports.html
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
