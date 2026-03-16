namespace CyberArk.Extensions.Plugin.Python4CPM
{
    public class EncryptedString
    {
        public EncryptedString(string value)
        {
            Value = value;
        }

        public string Value { get; }

        public override string ToString()
        {
            if (Value != null)
                return "[ENCRYPTED]";
            return "[NOT SET]";
        }
    }
}
