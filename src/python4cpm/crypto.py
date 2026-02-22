import sys
import ctypes
import ctypes.wintypes
import base64


class Crypto:
    if sys.platform == "win32":
        ENABLED = True
    else:
        ENABLED = False

    class DataBlob(ctypes.Structure):
        _fields_ = [
            ("cbData", ctypes.wintypes.DWORD),
            ("pbData", ctypes.POINTER(ctypes.c_ubyte))
        ]

    @classmethod
    def _verify_enabled(cls):
        if not cls.ENABLED:
            raise OSError("DPAPI is only available on Windows")

    @classmethod
    def decrypt(cls, base64_enc_string: str) -> str:
        cls._verify_enabled()
        encrypted_bytes = base64.b64decode(base64_enc_string.encode())
        buffer = ctypes.create_string_buffer(encrypted_bytes)
        input_blob = cls.DataBlob(
            len(encrypted_bytes),
            ctypes.cast(buffer, ctypes.POINTER(ctypes.c_ubyte))
        )
        output_blob = cls.DataBlob()
        crypt_res = ctypes.windll.crypt32.CryptUnprotectData(
            ctypes.byref(input_blob),
            None,
            None,
            None,
            None,
            0,
            ctypes.byref(output_blob)
        )
        if crypt_res:
            plaintext = ctypes.string_at(output_blob.pbData, output_blob.cbData)
            ctypes.windll.kernel32.LocalFree(output_blob.pbData)
            return plaintext.decode("utf-16-le")
        else:
            raise ctypes.WinError()

    @classmethod
    def encrypt(cls, plaintext: str) -> str:
        cls._verify_enabled()
        plain_bytes = plaintext.encode("utf-16-le")
        buffer = ctypes.create_string_buffer(plain_bytes)
        input_blob = cls.DataBlob(
            len(plain_bytes),
            ctypes.cast(buffer, ctypes.POINTER(ctypes.c_ubyte))
        )
        output_blob = cls.DataBlob()
        crypt_res = ctypes.windll.crypt32.CryptProtectData(
            ctypes.byref(input_blob),
            None,
            None,
            None,
            None,
            0,
            ctypes.byref(output_blob)
        )
        if crypt_res:
            encrypted = ctypes.string_at(output_blob.pbData, output_blob.cbData)
            ctypes.windll.kernel32.LocalFree(output_blob.pbData)
            return base64.b64encode(encrypted).decode()
        else:
            raise ctypes.WinError()
