using System;

namespace CyberArk.Extensions.Plugin.Python4CPM
{
    public class EncryptedString
    {
        public string Value { get; }

        public EncryptedString(string value)
        {
            Value = value;
        }

        public override string ToString()
        {
            if (Value != null)
                return "[ENCRYPTED]";
            return "[NOT SET]";
        }
    }
}
