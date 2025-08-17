### 1️⃣ Remove broken Python 3.11.8
```
pyenv uninstall -f 3.11.8
```

### 2️⃣ Install required build dependencies (macOS Homebrew)
```
brew install readline xz zlib tcl-tk openssl@3
```

### 3️⃣ Reinstall Python 3.11.8 with proper env flags
```env \
  LDFLAGS="-L/opt/homebrew/opt/zlib/lib -L/opt/homebrew/opt/openssl@3/lib" \
  CPPFLAGS="-I/opt/homebrew/opt/zlib/include -I/opt/homebrew/opt/openssl@3/include" \
  PKG_CONFIG_PATH="/opt/homebrew/opt/zlib/lib/pkgconfig:/opt/homebrew/opt/openssl@3/lib/pkgconfig" \
  pyenv install 3.11.8
  ```

### 4️⃣ Set 3.11.8 as local Python version for the project
```pyenv local 3.11.8
pyenv rehash
```

### 5️⃣ Verify correct Python
```
python --version
python3 --version
which python
```

### 6️⃣ Remove old venv if exists
```
rm -rf venv311
```

### 7️⃣ Create new virtual environment
```
python -m venv venv311
```

### 8️⃣ Activate venv
```
source venv311/bin/activate
```

### 9️⃣ Upgrade pip and setuptools
```
pip install --upgrade pip setuptools wheel
```

###  🔟 Optional: Install project requirements
```
pip install -r requirements.txt
```