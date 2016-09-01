# -*- mode: python -*-

block_cipher = None


a = Analysis(['run.py'],
             pathex=['D:\\Projects\\dev\\rsteditor-qt'],
             binaries=[],
             datas=[('rsteditor\\share', 'share')],
             hiddenimports=['rsteditor.scilexer.scilexerrest_py'],
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
          name='rsteditor',
          debug=False,
          strip=False,
          upx=False,
          console=False,
          icon='rsteditor\\share\\pixmaps\\rsteditor-text-editor.ico')
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=False,
               name='rsteditor')
