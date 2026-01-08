# 🚀 Wekeza Business Banking Portal - Installation Guide

![Installation Guide](https://img.shields.io/badge/Installation-Guide-blue?style=for-the-badge&logo=windows)
![Port 8504](https://img.shields.io/badge/Port-8504-orange?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Production%20Ready-success?style=for-the-badge)

## 📋 Table of Contents
1. [System Requirements](#-system-requirements)
2. [Pre-Installation Checklist](#-pre-installation-checklist)
3. [Step-by-Step Installation](#-step-by-step-installation)
4. [Database Setup](#-database-setup)
5. [Application Configuration](#-application-configuration)
6. [Starting the Portal](#-starting-the-portal)
7. [Verification & Testing](#-verification--testing)
8. [Troubleshooting](#-troubleshooting)
9. [Production Deployment](#-production-deployment)
10. [Maintenance & Updates](#-maintenance--updates)

---

## 💻 System Requirements

### 🖥️ **Minimum Requirements**
```
Operating System: Windows 10/11, macOS 10.15+, Ubuntu 18.04+
Processor:        Intel i3 / AMD Ryzen 3 (2.0GHz+)
Memory:           4GB RAM
Storage:          10GB free space
Network:          Broadband internet connection
Browser:          Chrome 90+, Firefox 88+, Safari 14+, Edge 90+
```

### 🚀 **Recommended Requirements**
```
Operating System: Windows 11, macOS 12+, Ubuntu 20.04+
Processor:        Intel i5 / AMD Ryzen 5 (3.0GHz+)
Memory:           8GB RAM
Storage:          50GB SSD
Network:          High-speed internet connection
Browser:          Latest versions of Chrome, Firefox, Safari, Edge
```

### 🛠️ **Software Dependencies**
- **Python 3.8+** (Required)
- **MySQL 8.0+** (Required)
- **Git** (Optional, for version control)
- **Visual Studio Code** (Optional, for development)

---

## ✅ Pre-Installation Checklist

### 📦 **Required Software**
- [ ] Python 3.8 or higher installed
- [ ] MySQL Server 8.0+ running
- [ ] pip (Python package manager) available
- [ ] Administrative privileges on the system
- [ ] Internet connection for package downloads

### 🗃️ **Database Prerequisites**
- [ ] MySQL service running on localhost:3306
- [ ] Root access to MySQL server
- [ ] `wekeza_dfs_db` database created
- [ ] Sufficient disk space for database growth

### 🌐 **Network Prerequisites**
- [ ] Port 8504 available and not blocked by firewall
- [ ] Internet access for external API calls
- [ ] Network access to MySQL server
- [ ] SMTP server configured (for email notifications)

---

## 🔧 Step-by-Step Installation

### **Step 1: Verify Python Installation**

#### Windows:
```cmd
# Check Python version
python --version
# Should show Python 3.8.x or higher

# Check pip installation
pip --version
```

#### macOS/Linux:
```bash
# Check Python version
python3 --version
# Should show Python 3.8.x or higher

# Check pip installation
pip3 --version
```

**If Python is not installed:**
- **Windows**: Download from https://python.org/downloads/
- **macOS**: Use Homebrew: `brew install python3`
- **Linux**: Use package manager: `sudo apt install python3 python3-pip`

### **Step 2: Navigate to Project Directory**

```bash
# Navigate to the Wekeza DFS Platform directory
cd "F:\Software Engineering\Banking\Wekeza Bank DFS System\wekeza_dfs_platform"

# Verify you're in the correct directory
dir  # Windows
ls   # macOS/Linux

# You should see folders like 03_Source_Code, and files like start_business_portal.bat
```

### **Step 3: Install Required Python Packages**

#### Option A: Install Individual Packages
```bash
pip install streamlit==1.28.0
pip install mysql-connector-python==8.2.0
pip install pandas==2.1.0
pip install uuid
pip install datetime
```

#### Option B: Create and Use Requirements File
```bash
# Create requirements.txt file
echo streamlit==1.28.0 > requirements.txt
echo mysql-connector-python==8.2.0 >> requirements.txt
echo pandas==2.1.0 >> requirements.txt

# Install from requirements file
pip install -r requirements.txt
```

#### Verify Installation:
```bash
# Test imports
python -c "import streamlit, mysql.connector, pandas; print('All packages installed successfully!')"
```

### **Step 4: Verify Directory Structure**

Ensure your directory structure looks like this:
```
wekeza_dfs_platform/
├── 03_Source_Code/
│   └── web_portal_business/
│       ├── business_app.py
│       ├── business_portal_sections.py
│       ├── business_insurance_sections.py
│       ├── business_settings_sections.py
│       ├── BUSINESS_BANKING_README.md
│       └── INSTALLATION_GUIDE.md
├── start_business_portal.bat
└── [other files and folders]
```

---

## 🗄️ Database Setup

### **Step 1: Start MySQL Service**

#### Windows:
```cmd
# Start MySQL service
net start mysql80

# Or use Services.msc to start MySQL80 service
```

#### macOS:
```bash
# Start MySQL using Homebrew
brew services start mysql

# Or use System Preferences > MySQL
```

#### Linux:
```bash
# Start MySQL service
sudo systemctl start mysql
sudo systemctl enable mysql
```

### **Step 2: Connect to MySQL**

```bash
# Connect to MySQL as root
mysql -u root -p

# Enter your MySQL root password when prompted
```

### **Step 3: Create Database and Verify Tables**

```sql
-- Create database if it doesn't exist
CREATE DATABASE IF NOT EXISTS wekeza_dfs_db;

-- Use the database
USE wekeza_dfs_db;

-- Verify required tables exist
SHOW TABLES;

-- You should see tables like:
-- businesses, accounts, transactions, users, user_policies, loan_applications, etc.

-- If tables don't exist, run the database setup scripts first
-- Exit MySQL
EXIT;
```

### **Step 4: Test Database Connection**

Create a test file to verify database connectivity:

```python
# Create test_db_connection.py
import mysql.connector

try:
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='root',  # Replace with your MySQL password
        database='wekeza_dfs_db'
    )
    
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM businesses")
    result = cursor.fetchone()
    
    print(f"✅ Database connection successful!")
    print(f"📊 Found {result[0]} businesses in database")
    
    conn.close()
    
except Exception as e:
    print(f"❌ Database connection failed: {e}")
```

```bash
# Run the test
python test_db_connection.py
```

---

## ⚙️ Application Configuration

### **Step 1: Configure Database Connection**

Edit the database connection in `business_app.py`:

```python
# Open business_app.py and locate the get_db_connection function
def get_db_connection():
    try:
        return mysql.connector.connect(
            host='localhost',        # Your MySQL host
            user='root',            # Your MySQL username
            password='root',        # Your MySQL password
            database='wekeza_dfs_db' # Your database name
        )
    except Exception as e:
        st.error(f"Database connection failed: {e}")
        return None
```

### **Step 2: Configure Application Settings**

Create a `.streamlit/config.toml` file in the business portal directory:

```toml
[server]
port = 8504
address = "localhost"
maxUploadSize = 200
enableCORS = false
enableXsrfProtection = true

[browser]
gatherUsageStats = false
showErrorDetails = true

[theme]
primaryColor = "#1f77b4"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f0f2f6"
textColor = "#262730"
```

### **Step 3: Environment Variables (Optional)**

Create a `.env` file for sensitive configuration:

```bash
# Database Configuration
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=root
DB_NAME=wekeza_dfs_db

# Application Configuration
APP_PORT=8504
APP_HOST=localhost
DEBUG_MODE=False

# Security Configuration
SESSION_TIMEOUT=3600
MAX_LOGIN_ATTEMPTS=3
ENABLE_2FA=True
```

---

## 🚀 Starting the Portal

### **Method 1: Using Batch File (Windows - Recommended)**

```cmd
# Navigate to the main directory
cd "F:\Software Engineering\Banking\Wekeza Bank DFS System\wekeza_dfs_platform"

# Run the batch file
.\start_business_portal.bat

# The portal should start and display:
# Starting Wekeza Business Banking Portal...
# You can now view your Streamlit app in your browser.
# Local URL: http://localhost:8504
```

### **Method 2: Direct Command**

```bash
# Navigate to the business portal directory
cd "F:\Software Engineering\Banking\Wekeza Bank DFS System\wekeza_dfs_platform\03_Source_Code\web_portal_business"

# Start the application
python -m streamlit run business_app.py --server.port 8504

# Alternative using streamlit directly
streamlit run business_app.py --server.port 8504
```

### **Method 3: Using Python Script**

Create a `start_portal.py` file:

```python
import subprocess
import sys
import os

def start_business_portal():
    try:
        # Change to the correct directory
        os.chdir("03_Source_Code/web_portal_business")
        
        # Start the Streamlit application
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            "business_app.py", "--server.port", "8504"
        ])
        
    except Exception as e:
        print(f"Error starting portal: {e}")

if __name__ == "__main__":
    start_business_portal()
```

```bash
# Run the Python script
python start_portal.py
```

---

## ✅ Verification & Testing

### **Step 1: Access the Portal**

1. **Open your web browser**
2. **Navigate to**: http://localhost:8504
3. **Verify the page loads** with the Wekeza Business Banking interface

### **Step 2: Test Login Functionality**

#### Default Test Credentials:
- **Username**: davidmtune@gmail.com
- **Password**: business123

#### Login Process:
1. Click on the **"Login"** tab
2. Enter the test credentials
3. Click **"Login"** button
4. Verify successful login and dashboard access

### **Step 3: Test Core Features**

#### Test Account Overview:
1. Navigate to **"Accounts & Cash"** tab
2. Verify account balance displays correctly
3. Check recent transactions appear

#### Test Payment Functionality:
1. Go to **"Payments & Transfers"** tab
2. Try creating a test payment
3. Verify form validation works

#### Test Settings Access:
1. Navigate to **"Settings"** tab
2. Verify all settings sections load
3. Test form submissions

### **Step 4: Network Access Test**

Test external network access:
```bash
# Test from another device on the same network
# Replace 192.168.100.29 with your actual IP address
http://192.168.100.29:8504
```

---

## 🔧 Troubleshooting

### **Common Issues & Solutions**

#### **Issue 1: Port 8504 Already in Use**
```
Error: Port 8504 is already in use
```

**Solution:**
`ietary.* proprential andonfidguide is cion  installatved. Thiser restsghBank. All ri2026 Wekeza *© 

o.ke

---.ct@wekezebank suppor**:*SupportME.md
- *NG_READBANKINESS_n**: BUSIio**Documentat3
- 12m / business@gmail.cotunevidm*: da**Login*4
- lhost:850 http://locaURL**:- **Portal 
k Access:**uic
### **Qrtal
sing the pour team on uyog**: Train nin5. **Traiquired
stems if re syer bankingth othwi: Connect on**rati
4. **Integferencesrity pred secuification anjust nottings**: Adtomize Set*Cusded
3. *nees if usersiness onal bu additi Set upsers**:ure U*Config2. *nality
unctiond test fs augh all tabthroate NavigFeatures**: re the *Explo *
1. Steps:***Next## **! 

#Portal*ess Banking usinkeza B **Weed they installfullve successYou ha

tions!lagratu

## 🎉 Conhed

---tablises esp procedurBackup
- [ ] logging setund onitoring a] M
- [  configuredmanagementcess d
- [ ] Proing completeenhardurity Sec
- [ ] edion applifiguratuction conProd ]  [**
-(Optional)Production d)

### **needeerified (if  access vtworked
- [ ] Nes testre feature
- [ ] Corkingtionality wo] Login funct:8504
- [ p://localhos httessible at] Portal acc
- [ esting***T

### * needed)s set (ift variableonmen[ ] Envireted
- tion complranfiguon co Applicati [ ] tested
-nnectionatabase co- [ ] Dified
ure vertructectory soject dir Pr
- [ ]**stallation
### **In
s availablerivilegeistrative p- [ ] Adminailable
rt 8504 avd
- [ ] Pos installekagequired pacle
- [ ] Reaccessibg and runnin8.0+ MySQL - [ ] erified
led and v instalPython 3.8+*
- [ ] tion*lanstal*Pre-It

### *Checklisllation 
## ✅ Instast

---
ull requemit a ply
5. Subought thor
4. Tesesr changouMake y
3. e brancha featurate 
2. Crerepositoryk the or
1. Fe project:te to thontribu*

To contributing***C### 

ableapplics**: If nshot
6. **Screeppensally ha actur**: WhatBehavioal ctuen
5. **Auld happ: What sho**viorhaExpected Bes
4. **n stepoductioreprtailed *: Deoduce*teps to Repr
3. **Sgs loete errorpl: Comessages**. **Error Mr
2n, browse versioOS, Pythonion**: nformatem I **Systlude:
1.se inc, plearting issuesen repo

Whsues**ng Is **Reporti

###ing`wekeza-bankions with `stag queflow**: Ttack Overons
- **S discussimunityum**: ComFor*Developer  *s
-re requestnd featu bugs a**: Reportes Issuub **GitHity:
-Commun
#### 
3 45812 +254 700 *:rgency*
- **Eme 123 456: +254 700- **Phone**nk.co.ke
bart@wekezesuppo*Email**: 
- * Channels:#### Supportpoint

 `/docs` endatle n**: Availabntatiocume
- **API Don guideallatio: This instUIDE.md**ON_G*INSTALLATIon
- *entatire documfeatuete **: Complmd
- **README.ntation:### Docume
# Help**
Getting
### ** & Help
## 📞 Support

---```

"
ESSLIST;SHOW PROCot -p -e "mysql -u roabase
onitor dat.log

# M_portalbusiness-f 
tail tion logsicapltor ap

# Moniee -m
df -h
fropsources
htr system resh
# Monitog:
```ba Monitorin### System
```

#s}"): {detail {action}erformedd} per {user_ifo(f"Us  logging.intails):
  , de, actionidity(user_r_activ log_usevities
defg user acti

# Lossage)s'
)%(melname)s -  - %(levesctime)s format='%(ag.INFO,
   el=loggin   lev
 al.log',ess_port'busine=lenam
    finfig(ng.basicCoging
loggiure logfigime

# Conort tging
imp
import logness_app.py Add to busin
#hoyt
```png:nitorication Mopli## Apts**

## & Aleritoring**Mon`

###  status
``pm2yment
eplofy d# Veriusiness

wekeza-btart  sication
pm2ed applpdat u# Starts

a-businesez wekm2 stopication
p applStop current
# s
```bashate: Deploy Updp 4
#### Stees
```
eatur core fts, andn, paymengiTest lo
# nalityfy functio Veri05

#rt 85--server.pos_app.py esusin blit runamtre
python -m sest modein t
# Run `bashs
``est Update T#### Step 3:
```

ements.txtequirde -r r--upgra install 
pipckages padate Python
# Upin
rigin ma
git pull o Git) usinghanges (ifll latest c# Puash
``bplication
`Ap2: Update tep ### S
#`
d).sql
``%Y%m%date +ckup_$(_baza_dfs_dbs_db > wekep wekeza_dfmp -u root -ase
mysqldutabBackup da%m%d)

# (date +%Ys_backup_$al_businesortb_p/werce_Code_Souess 03l_busintaode/web_porce_Cr 03_Sour -s
cpfileication plckup apbash
# Ballation
```taCurrent Insp 1: Backup te

#### Socedure**te Pr
### **Updaudit
urity an
- [ ] Secizationce optim] Performa
- [ tate logs roeview andges
- [ ] Rn packahoyt P [ ] Updately:
-# Month
###
p database] Backusage
- [ disk space u[ ] Check kages
- ystem pac s- [ ] Updatey logs
curitiew se ] Revekly:
- [
#### Weogs
ty lser activi ] Check u [ity
-connectivtabase fy da[ ] Veriage
- rce us resour systemito
- [ ] Monr errorsion logs foapplicatck Chely:
- [ ]  Dai
####asks**
ntenance Tar Maigul# **Re

##pdatesnce & U🔄 Maintena-

## 

--}
}
```
    ade;http_upgrss $e_bypay_cachrox        po $scheme;
otrwarded-Prer X-Foheady_set_     prox
   warded_for;_ford_xproxy_ad-For $dedarrw-Fo_header X proxy_set      r;
 mote_addIP $reer X-Real-_head  proxy_set    t;
  ost $hos_header H proxy_set
       n 'upgrade';Connectioader t_he  proxy_se   rade;
   e $http_upgader Upgradproxy_set_he       
 rsion 1.1;tp_veoxy_ht        pr4;
50localhost:8ttp://y_pass h    prox {
    on /    locati
    
ke;.co.wekezebanksiness.ver_name bu
    seren 80;
    list{server 
-business/wekeza-available/sitesginx
# /etc/ninx
```ngfiguration:## Nginx Con*

##(Optional)*tup Seroxy Reverse PStep 4: 
### **tup
```

pm2 starm2 saveguration
pPM2 confi Save iness

#keza-bus--name weort 8504"  --server.piness_app.pyun buseamlit r -m strt "pythonstarpm2 PM2
h  witonapplicatirt 
# Stam2
nstall -g pl PM2
npm iInstal`bash
# ``tform):
 (Cross-pla# Using PM2

###```iness
ekeza-bustus w staemctludo syst
siness-busza start wekesystemctlsudo siness
buekeza-enable wl o systemctervice
sudnd start sEnable a``bash
# 
`
et
```r.targBy=multi-usetedanall]
W10

[InststartSec=ways
Re=al504
Restartport 8er.rv-seapp.py -s_ines run busm streamlithon3 -sr/bin/pytExecStart=/uess
l_businortade/web_pSource_Co/03_t/wekezay=/optorecDirWorkingekeza
le
User=wpe=simpService]
Tyce

[sql.serviet mywork.targ=net
Afterg Portalkin BannesssiBueza tion=Wekit]
Descripce
[Unvisiness.ser/wekeza-butemystemd/sysi
# /etc/s
```in): (Linuxemd syst# Usingt**

###emennagocess MaPrp 3: ### **Ste


```e_key())generatnet.ET_KEY', Ferenv('SECR = os.getEYECRET_K')
Sordasswfault_p, 'de_PASSWORD'getenv('DBos.WORD = ta
DB_PASSitive dar sensriables fovironment vaen
# Use  Fernet
rt.fernet impoyptography
from crrt osction
imporoduor p.py fsiness_appate bu# Updn
:
```pythoion Security## Applicat##ES;
```

PRIVILEGLUSH t';
Focalhosusiness'@'lza_bTO 'wekes_db.* ON wekeza_dfE , DELET UPDATERT,SESELECT, INT ANre';
GRword_here_passY 'secuENTIFIED Bost' IDlocalhs'@'za_busines USER 'wekeREATEase user
Cdatabated dicCreate de```sql
-- ty:
 Securiatabase D
####ing**
ardenSecurity Hep 2: *St
### *
```
passwordecure-SWORD=your-srt DB_PASr
expose-u-dbproductionR=your- DB_USEt
exporthosb-n-dproductioyour-rt DB_HOST=alse
expoBUG=Fort DEuction
expRONMENT=prodexport ENVIbles
onment varianviruction e
# Prod:
```bashVariablesent vironm
#### En
o"
```evel = "infgger]
l
[lo = false
rDetailsshowErro= false
ageStats ]
gatherUsrowser

[b= trues eadlese
htion = truecProt
enableXsrfS = falsebleCORe = 200
enaizloadS0"
maxUp0.0.0. "ddress =8504
a
port = ver]
[sertionduc for profig.tomlconeamlit/oml
# .str
```t:gurationuction Confieate Prod
#### Cr Setup**
ronmentction Envip 1: Produ **Stet

###eploymenoduction D🏭 Pr# 

#

---gs/`streamlit/lo~/.ux**: ` **macOS/Lin\logs\`
-mlitstreaILE%\.`%USERPROFdows**:  **Win:
-ationrror inform etailediles for de
Check log f
*Log Files**# *
##ue)
```
ils', TrwErrorDetaclient.shotion('
st.set_opmodebug ble denaas st

# Eeamlit 
import str_app.pyto businessAdd # python


```ormation:or inferrdetailed ug mode for  deb

Enableg Mode**
### **Debuons
```
icatilowed applython to aldd Pions
# A> Opt > Firewall vacy Pri> Security &erences tem Pref# SysacOS


# m8504ufw allow UFW
sudo 

# Linux rewallDefender Fiws ndon Wi8504 ifor port nbound rule Add ill
# ndows Firewa
# Wi```bashlution:**
```

**Sovices
er derom othl fcess porta ac CannotError:
```
ss**Acce Blocking allrew*Issue 5: Fi# *
```

###ormlatf_pekeza_dfspath/to/wR:$USER /USER $hown -o cal.bat
sud_portinessart_bus+x stchmod x/macOS)
ions (Linule permisschange fi# Or strator

un as Admini Prompt > Rmandclick Comght-ws)
# Riindo(Wstrator dmini# Run as a
```bash
*Solution:**
*tion
```
icapplrting the aen stawhied ssion den Permior:
```
Erron Denied**Permissiue 4: ## **Iss
##amlit
```
re | grep st
pip listlationinstal
# Verify s
on pandaor-pyth-connect mysqleamlitstrgrade nstall --upages
pip ickired pall requh
# Reinsta``basution:**
`

**Soleamlit'
```d 'stre name modulndError: NouleNotFouod
Error: M`` Error**
`t FoundNo 3: Module ### **Issue
```

#LEGES;PRIVIH ;
FLUSalhost'_user'@'loc'wekezadfs_db.* TO ON wekeza_S LL PRIVILEGE';
GRANT A_passwordwekezaY 'ENTIFIED Bst' ID'@'localhoeza_userR 'wekATE USE
CREw usereate a ne- Or crS;

-RIVILEGELUSH P';
FBY 'rootNTIFIED ' IDE'localhostot'@USER 'roER ord
ALTsswQL root paySReset M
-- 
```sqltion:**olu`

**Salhost'
``root'@'locser 'or uss denied failed: Acceion f connect Database
Error:```
ed**n Faile ConnectioasabDatue 2: ss#### **I```

 8505
-server.portapp.py -ness_ busit runreamli
stent portuse a differ
# Or OS/Linux
  # mac          ID>     <P9 ws
kill - # Windo      ID> /F /PID <Paskkill e process
t
# Kill thcOS/Linux
       # ma      04    lsof -i :85ndows
  # Wistr :8504 | findanot -04
netsta 85port using cessFind probash
# ``