using System;

namespace CyberArk.Extensions.Plugin.Python4CPM
{
    public class EncryptedString
    {
        public string Secret { get; }

        public EncryptedString(string secret)
        {
            Secret = secret;
        }
    }
}
