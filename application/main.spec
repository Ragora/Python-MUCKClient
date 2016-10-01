# -*- mode: python -*-

block_cipher = None


a = Analysis(['main.py'],
             pathex=['/home/ragora/Desktop/Python-MUCKClient/application'],
             binaries=None,
             datas=[("config.txt", "."), ("ui/", "ui")],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          name='Client',
          debug=False,
          icon="ui/logo.ico",
          strip=False,
          upx=True,
          console=False )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name='main')
