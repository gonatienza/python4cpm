using System;
using System.Runtime.InteropServices;
using System.Security;
using System.Security.Cryptography;

namespace CyberArk.Extensions.Plugin.Python4CPM
{
    public static class Crypto
    {
        public static Secret Encrypt(SecureString secureStr)
        {
            IntPtr unmanagedPtr = IntPtr.Zero;
            try
            {
                unmanagedPtr = Marshal.SecureStringToGlobalAllocUnicode(secureStr);
                int byteCount = secureStr.Length * 2;
                byte[] plainBytes = new byte[byteCount];
                try
                {
                    Marshal.Copy(unmanagedPtr, plainBytes, 0, byteCount);
                    byte[] encrypted = ProtectedData.Protect(
                        plainBytes,
                        null,
                        DataProtectionScope.CurrentUser);
                    return new Secret(Convert.ToBase64String(encrypted));
                }
                finally
                {
                    Array.Clear(plainBytes, 0, plainBytes.Length);
                }
            }
            finally
            {
                if (unmanagedPtr != IntPtr.Zero)
                    Marshal.ZeroFreeGlobalAllocUnicode(unmanagedPtr);
            }
        }
    }
}
