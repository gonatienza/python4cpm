using System.Security;

namespace CyberArk.Extensions.Plugin.Python4CPM
{
    public class Secret
    {
        public Secret(string value)
        {
            Value = value;
        }

        public string Value { get; }

        public string Get()
        {
            return Crypto.Decrypt(Value);
        }

        public override string ToString()
        {
            if (Value != null)
                return "[ENCRYPTED]";
            return "[NOT SET]";
        }
    }

    public class Password : Secret
    {
        public Password(string value) : base(value) { }

        public static Password FromSecureString(SecureString secureStr)
        {
            Secret secret = Crypto.Encrypt(secureStr);
            return new Password(secret.Value);
        }
    }

    public class NewPassword : Secret
    {
        public NewPassword(string value) : base(value) { }

        public static NewPassword FromSecureString(SecureString secureStr)
        {
            Secret secret = Crypto.Encrypt(secureStr);
            return new NewPassword(secret.Value);
        }
    }

    public class ReturnedPassword : Secret
    {
        public ReturnedPassword(string value) : base(value) { }
    }
}
