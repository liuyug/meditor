# -*- mode: python -*-

block_cipher = None


a = Analysis(['run.py'],
             pathex=['D:\\Projects\\dev\\rsteditor-qt'],
             binaries=[],
             datas=[('meditor\\share', 'share')],
             hiddenimports=['meditor.scilib.scilexerrest_py'],
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
          name='meditor',
          debug=False,
          strip=False,
          upx=False,
          console=False,
          icon='meditor\\share\\pixmaps\\meditor-text-editor.ico')
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=False,
               name='meditor')
