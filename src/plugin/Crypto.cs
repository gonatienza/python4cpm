using System;
using System.Diagnostics;
using System.Security;
using System.Security.Cryptography;
using System.Text;
using CyberArk.Extensions.Utilties.Reader;

namespace CyberArk.Extensions.Python4CPM
{
    public class Crypto
    {
        public static string Encrypt(SecureString secureStr)
        {
            string plainText = secureStr.convertSecureStringToString();
            byte[] plainBytes = Encoding.UTF8.GetBytes(plainText);
            byte[] encrypted = ProtectedData.Protect(plainBytes, null, DataProtectionScope.CurrentUser);
            Array.Clear(plainBytes, 0, plainBytes.Length);
            string base64String = Convert.ToBase64String(encrypted);
            return base64String;
        }
    }
}
