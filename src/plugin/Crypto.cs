using System;
using System.Security;
using System.Security.Cryptography;
using System.Runtime.InteropServices;

namespace CyberArk.Extensions.Python4CPM
{
    public class Crypto
    {
        public static string Encrypt(SecureString secureStr)
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
                    return Convert.ToBase64String(encrypted);
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
