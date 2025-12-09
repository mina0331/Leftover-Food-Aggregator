# Project Dependencies, Frameworks, Packages, and Licenses

This document lists all libraries, frameworks, and packages used in this Django project, along with their licenses and where to find license information.

**Last Updated:** Based on `requirements.txt` and installed packages

---

## Primary Framework

### Django
- **Version:** 4.2.25
- **License:** BSD-3-Clause
- **Homepage:** https://www.djangoproject.com/
- **License Location:** 
  - `venv/lib/python3.11/site-packages/django-4.2.25.dist-info/LICENSE`
  - https://github.com/django/django/blob/main/LICENSE
- **Purpose:** Main web framework for the application

---

## Core Dependencies

### asgiref
- **Version:** 3.10.0
- **License:** BSD-3-Clause
- **Homepage:** https://github.com/django/asgiref
- **Purpose:** ASGI specification reference implementation

### sqlparse
- **Version:** 0.5.3
- **License:** BSD-3-Clause (license info in package metadata)
- **Homepage:** https://github.com/andialbrecht/sqlparse
- **Purpose:** SQL parser for Django

### typing_extensions
- **Version:** 4.15.0
- **License:** Python Software Foundation License
- **Homepage:** https://github.com/python/typing_extensions
- **Purpose:** Backported type hints for older Python versions

---

## Authentication & Social Login

### django-allauth
- **Version:** 65.12.1
- **License:** MIT
- **Homepage:** https://allauth.org
- **License Location:**
  - `venv/lib/python3.11/site-packages/django_allauth-65.12.1.dist-info/LICENSE`
  - https://github.com/pennersr/django-allauth/blob/main/LICENSE
- **Purpose:** Integrated authentication solution (local accounts, social accounts, email verification)

### social-auth-app-django
- **Version:** 5.4.3
- **License:** BSD
- **Homepage:** https://github.com/python-social-auth/social-app-django
- **Purpose:** Social authentication for Django

### social-auth-core
- **Version:** 4.7.0
- **License:** BSD
- **Homepage:** https://github.com/python-social-auth/social-core
- **Purpose:** Core functionality for social authentication

### oauthlib
- **Version:** 3.3.1
- **License:** BSD-3-Clause
- **Homepage:** https://github.com/oauthlib/oauthlib
- **License Location:**
  - `venv/lib/python3.11/site-packages/oauthlib-3.3.1.dist-info/licenses/LICENSE`
- **Purpose:** OAuth implementation library

### requests-oauthlib
- **Version:** 2.0.0
- **License:** ISC
- **Homepage:** https://github.com/requests/requests-oauthlib
- **Purpose:** OAuth for Python Requests

### PyJWT
- **Version:** 2.10.1
- **License:** MIT
- **Homepage:** https://github.com/jpadilla/pyjwt
- **Purpose:** JSON Web Token implementation

### python3-openid
- **Version:** 3.2.0
- **License:** Apache License 2.0 (license file present but metadata shows UNKNOWN)
- **Homepage:** https://github.com/necaris/python3-openid
- **License Location:**
  - `venv/lib/python3.11/site-packages/python3_openid-3.2.0.dist-info/LICENSE`
- **Purpose:** OpenID support for Python 3

---

## Database

### psycopg2
- **Version:** 2.9.10
- **License:** LGPL with exceptions (allows linking in proprietary applications)
- **Homepage:** https://psycopg.org/
- **License Location:**
  - `venv/lib/python3.11/site-packages/psycopg2_binary-2.9.10.dist-info/LICENSE`
- **Purpose:** PostgreSQL adapter for Python

### psycopg2-binary
- **Version:** 2.9.10
- **License:** LGPL with exceptions
- **Purpose:** Pre-compiled binary distribution of psycopg2

### psycopg
- **Version:** 3.2.10
- **License:** LGPL with exceptions
- **Homepage:** https://www.psycopg.org/
- **Purpose:** PostgreSQL adapter (version 3)

### psycopg-binary
- **Version:** 3.2.10
- **License:** LGPL with exceptions
- **License Location:**
  - `venv/lib/python3.11/site-packages/psycopg_binary-3.2.10.dist-info/licenses/LICENSE.txt`
- **Purpose:** Pre-compiled binary distribution of psycopg

### dj-database-url
- **Version:** 3.0.1
- **License:** BSD
- **Homepage:** https://github.com/jacobian/dj-database-url
- **Purpose:** Database URL configuration helper for Django

---

## HTTP & Networking

### requests
- **Version:** 2.32.5
- **License:** Apache-2.0
- **Homepage:** https://requests.readthedocs.io
- **License Location:**
  - `venv/lib/python3.11/site-packages/requests-2.32.5.dist-info/licenses/LICENSE`
  - https://github.com/psf/requests/blob/main/LICENSE
- **Purpose:** HTTP library for making requests

### urllib3
- **Version:** 2.5.0
- **License:** MIT
- **Homepage:** https://urllib3.readthedocs.io
- **License Location:**
  - `venv/lib/python3.11/site-packages/urllib3-2.5.0.dist-info/licenses/LICENSE.txt`
- **Purpose:** HTTP client library

### certifi
- **Version:** 2025.10.5
- **License:** MPL-2.0
- **Homepage:** https://github.com/certifi/python-certifi
- **Purpose:** SSL certificate bundle

### idna
- **Version:** 3.11
- **License:** BSD-3-Clause
- **Homepage:** https://github.com/kjd/idna
- **Purpose:** Internationalized Domain Names support

### charset-normalizer
- **Version:** 3.4.4
- **License:** MIT
- **Homepage:** https://github.com/Ousret/charset_normalizer
- **Purpose:** Character encoding detection

---

## Security & Cryptography

### cryptography
- **Version:** 46.0.3
- **License:** Apache-2.0 and BSD
- **Homepage:** https://github.com/pyca/cryptography
- **Purpose:** Cryptographic recipes and primitives

### cffi
- **Version:** 2.0.0
- **License:** MIT
- **Homepage:** https://cffi.readthedocs.io
- **Purpose:** Foreign Function Interface for Python

### pycparser
- **Version:** 2.23
- **License:** BSD-3-Clause
- **Homepage:** https://github.com/eliben/pycparser
- **Purpose:** C parser in Python (dependency of cffi)

### defusedxml
- **Version:** 0.7.1
- **License:** Python Software Foundation License
- **Homepage:** https://github.com/tiran/defusedxml
- **License Location:**
  - `venv/lib/python3.11/site-packages/defusedxml-0.7.1.dist-info/LICENSE`
- **Purpose:** XML parser that prevents XML attacks

---

## Image Processing

### Pillow
- **Version:** 10.4.0
- **License:** HPND (Historical Permission Notice and Disclaimer)
- **Homepage:** https://python-pillow.org
- **Purpose:** Image processing library

### qrcode
- **Version:** 8.2
- **License:** BSD
- **Homepage:** https://github.com/lincolnloop/python-qrcode
- **Purpose:** QR code generation

---

## Deployment & Server

### gunicorn
- **Version:** 23.0.0
- **License:** MIT
- **Homepage:** https://gunicorn.org
- **Purpose:** Python WSGI HTTP Server for production

### django-heroku
- **Version:** 0.3.1
- **License:** MIT
- **Homepage:** https://github.com/heroku/django-heroku
- **Purpose:** Heroku deployment configuration for Django

### whitenoise
- **Version:** 6.11.0
- **License:** MIT
- **Homepage:** https://whitenoise.readthedocs.io
- **Purpose:** Static file serving for Django

---

## Cloud Storage

### boto3
- **Version:** 1.35.0
- **License:** Apache License 2.0
- **Homepage:** https://github.com/boto/boto3
- **Purpose:** AWS SDK for Python

### django-storages
- **Version:** 1.14.2
- **License:** BSD-3-Clause
- **Homepage:** https://github.com/jschneier/django-storages
- **Purpose:** Django storage backends for cloud storage (S3, etc.)

### botocore
- **Version:** 1.35.99
- **License:** Apache License 2.0
- **Homepage:** https://github.com/boto/botocore
- **Purpose:** Low-level AWS service client (dependency of boto3)

### jmespath
- **Version:** 1.0.1
- **License:** MIT
- **Homepage:** https://github.com/jmespath/jmespath.py
- **Purpose:** JSON Matching Expressions (dependency of boto3)

### s3transfer
- **Version:** 0.10.4
- **License:** Apache License 2.0
- **Homepage:** https://github.com/boto/s3transfer
- **Purpose:** S3 transfer manager (dependency of boto3)

### python-dateutil
- **Version:** 2.9.0.post0
- **License:** Apache License 2.0 and BSD-3-Clause
- **Homepage:** https://github.com/dateutil/dateutil
- **Purpose:** Date utilities (dependency of boto3)

### six
- **Version:** 1.17.0
- **License:** MIT
- **Homepage:** https://github.com/benjaminp/six
- **Purpose:** Python 2 and 3 compatibility (dependency)

---

## Utilities

### packaging
- **Version:** 25.0
- **License:** Apache-2.0 and BSD-2-Clause (license info in package metadata)
- **Homepage:** https://github.com/pypa/packaging
- **Purpose:** Core utilities for Python packages

---

## Where to Find License Information

### In the Project:
1. **Installed Packages:**
   - Location: `venv/lib/python3.11/site-packages/*.dist-info/`
   - Each package's `.dist-info` directory contains:
     - `METADATA` file with license information
     - `LICENSE` or `LICENSE.txt` file (if included)
     - `licenses/` subdirectory (for some packages)

2. **Requirements File:**
   - Location: `requirements.txt` (project root)
   - Lists all package versions but not licenses

### Online Sources:
1. **PyPI (Python Package Index):**
   - https://pypi.org/
   - Search for package name → "License" section

2. **GitHub Repositories:**
   - Most packages have LICENSE files in their GitHub repos
   - Links provided in "Homepage" column above

3. **Package Documentation:**
   - Check package documentation sites (links in "Homepage" column)

---

## License Summary

| License Type | Count | Packages |
|-------------|-------|----------|
| MIT | ~15 | django-allauth, django-heroku, gunicorn, whitenoise, PyJWT, urllib3, cffi, charset-normalizer, jmespath, six, etc. |
| BSD / BSD-3-Clause | ~12 | Django, asgiref, sqlparse, social-auth packages, oauthlib, psycopg, idna, pycparser, qrcode, django-storages, etc. |
| Apache-2.0 | ~6 | requests, cryptography, python3-openid, boto3, botocore, s3transfer, packaging |
| LGPL / LGPLv3 | 4 | psycopg2, psycopg2-binary, psycopg, psycopg-binary |
| HPND | 1 | Pillow |
| Python Software Foundation (PSF) | 2 | typing_extensions, defusedxml |
| MPL-2.0 | 1 | certifi |
| ISC | 1 | requests-oauthlib |

---

## Notes

1. **Most packages are permissively licensed** (MIT, BSD, Apache-2.0), allowing commercial use and modification.

2. **LGPL packages (psycopg2/psycopg)** have exceptions that allow linking in proprietary applications without requiring your code to be open source.

3. **All licenses are compatible** for use in a Django web application.

4. **For production deployment**, ensure you comply with all license requirements, particularly:
   - Include license notices where required
   - Maintain copyright notices
   - Some licenses may require attribution

5. **To view a specific package's license:**
   ```bash
   pip show <package-name> | grep License
   ```

6. **To view license file directly:**
   ```bash
   cat venv/lib/python3.11/site-packages/<package>-<version>.dist-info/LICENSE
   ```

---

## Verification Commands

To verify installed packages and their licenses:

```bash
# Activate virtual environment
source venv/bin/activate

# List all packages with versions
pip list

# Show details for a specific package (including license)
pip show <package-name>

# Find all LICENSE files
find venv/lib/python3.11/site-packages -name "LICENSE*" -o -name "LICENCE*"
```

---

**Document Generated:** Based on `requirements.txt` and installed packages in virtual environment
**Project Location:** `/Users/leolee/UVA/Year3-2526/SWE/project-b-27`

