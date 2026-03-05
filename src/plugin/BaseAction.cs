using CyberArk.Extensions.Plugins.Models;
using CyberArk.Extensions.Utilties.Logger;
using CyberArk.Extensions.Utilties.Reader;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System;

namespace CyberArk.Extensions.Plugin.Python4CPM
{
    abstract public class BaseAction : AbsAction
    {
        private const string ENV_PREFIX = "PYTHON4CPM_";
        private const string ENV_ACTION = $"{ENV_PREFIX}ACTION";
        private const string ENV_USERNAME = $"{ENV_PREFIX}TARGET_USERNAME";
        private const string ENV_ADDRESS = $"{ENV_PREFIX}TARGET_ADDRESS";
        private const string ENV_PORT = $"{ENV_PREFIX}TARGET_PORT";
        private const string ENV_LOGON_USERNAME = $"{ENV_PREFIX}LOGON_USERNAME";
        private const string ENV_RECONCILE_USERNAME = $"{ENV_PREFIX}RECONCILE_USERNAME";
        private const string ENV_LOGGING = $"{ENV_PREFIX}LOGGING";
        private const string ENV_LOGGING_LEVEL = $"{ENV_PREFIX}LOGGING_LEVEL";
        private const string ENV_PASSWORD = $"{ENV_PREFIX}PASSWORD";
        private const string ENV_LOGON_PASSWORD = $"{ENV_PREFIX}LOGON_PASSWORD";
        private const string ENV_RECONCILE_PASSWORD = $"{ENV_PREFIX}RECONCILE_PASSWORD";
        private const string ENV_NEW_PASSWORD = $"{ENV_PREFIX}TARGET_NEW_PASSWORD";
        private const string PARAMS_PYTHON_EXE_PATH = "PythonExePath";
        private const string PARAMS_PYTHON_SCRIPT_PATH = "PythonScriptPath";
        private const string PARAMS_PYTHON_LOGGING = "PythonLogging";
        private const string PARAMS_PYTHON_LOGGING_LEVEL = "PythonLoggingLevel";
        private const string PROPERTIES_USERNAME = "username";
        private const string PROPERTIES_ADDRESS = "address";
        private const string PROPERTIES_PORT = "port";
        protected const int CLOSE_SUCCESS = 0;
        protected const int CLOSE_FAILED_UNRECOVERABLE = 8900;
        protected const int CLOSE_FAILED_RECOVERABLE = 8100;
        private const int PYTHON_CLOSE_SUCCESS = 10;
        public const int PYTHON_CLOSE_FAILED_UNRECOVERABLE = 89;
        public const int PYTHON_CLOSE_FAILED_RECOVERABLE = 81;
        private string PythonExePath = string.Empty;
        private string PythonScriptPath = string.Empty;
        private string Username = string.Empty;
        private string Address = string.Empty;
        private string Port = string.Empty;
        private string LogonUsername = string.Empty;
        private string ReconcileUsername = string.Empty;
        private string PythonLogging = string.Empty;
        private string PythonLoggingLevel = string.Empty;
        private EncryptedString CurrentPassword = new EncryptedString(string.Empty);
        private EncryptedString LogonCurrentPassword = new EncryptedString(string.Empty);
        private EncryptedString ReconcileCurrentPassword = new EncryptedString(string.Empty);
        private EncryptedString NewPassword = new EncryptedString(string.Empty);

        public BaseAction(List<IAccount> accountList, ILogger logger)
            : base(accountList, logger)
        {
        }

        protected abstract bool RequiresNewPassword
        {
            get;
        }

        private string GetLoggingValue(object obj)
        {
            string logValue;
            if (obj is EncryptedString enc && enc.Secret != string.Empty)
            {
                logValue = "[ENCRYPTED]";
            }
            else if (obj is string str && str != string.Empty)
            {
                logValue = $"'{str}'";
            }
            else
            {
                logValue = "[NOT SET]";
            }
            return logValue;
        }

        private void LogField(string name, object obj)
        {
            string logValue = GetLoggingValue(obj);
            Logger.WriteLine($"{name} -> {logValue}", LogLevel.INFO);
        }

        private void LogEnvVar(string name, object obj)
        {
            string logValue = GetLoggingValue(obj);
            Logger.WriteLine($"'{name}' -> {logValue}", LogLevel.INFO);
        }

        private string GetExtraInfoProp(BaseAccount account, string prop)
        {
            if (account?.ExtraInfoProp?.ContainsKey(prop) == true)
            {
                return account.ExtraInfoProp[prop];
            }
            else
            {
                return string.Empty;
            }
        }

        private string GetAccountProp(BaseAccount account, string prop)
        {
            if (account?.AccountProp?.ContainsKey(prop) == true)
            {
                return account.AccountProp[prop];
            }
            else
            {
                return string.Empty;
            }
        }

        private EncryptedString GetAccountPassword(BaseAccount account)
        {
            if (account?.CurrentPassword != null)
            {
                return Crypto.Encrypt(account.CurrentPassword);
            }
            else
            {
                return new EncryptedString(string.Empty);
            }
        }

        private EncryptedString GetNewPassword()
        {
            if (RequiresNewPassword)
            {
                if (TargetAccount?.NewPassword == null)
                {
                    throw new InvalidOperationException("Required new password is 'null'");
                }
                return Crypto.Encrypt(TargetAccount.NewPassword);
            }
            else
            {
                return new EncryptedString(string.Empty);
            }
        }

        private void GetParams()
        {
            PythonExePath = GetExtraInfoProp(TargetAccount, PARAMS_PYTHON_EXE_PATH);
            PythonScriptPath = GetExtraInfoProp(TargetAccount, PARAMS_PYTHON_SCRIPT_PATH);
            PythonLogging = GetExtraInfoProp(TargetAccount, PARAMS_PYTHON_LOGGING);
            PythonLoggingLevel = GetExtraInfoProp(TargetAccount, PARAMS_PYTHON_LOGGING_LEVEL);
            LogField(nameof(PythonExePath), PythonExePath);
            LogField(nameof(PythonScriptPath), PythonScriptPath);
            LogField(nameof(PythonLogging), PythonLogging);
            LogField(nameof(PythonLoggingLevel), PythonLoggingLevel);
            if (!File.Exists(PythonExePath))
                throw new FileNotFoundException($"{PARAMS_PYTHON_EXE_PATH}: '{PythonExePath}' not found");
            if (!File.Exists(PythonScriptPath))
                throw new FileNotFoundException($"{PARAMS_PYTHON_SCRIPT_PATH}: '{PythonScriptPath}' not found");
        }

        private void GetAccountData()
        {
            Username = GetAccountProp(TargetAccount, PROPERTIES_USERNAME);
            Address = GetAccountProp(TargetAccount, PROPERTIES_ADDRESS);
            Port = GetAccountProp(TargetAccount, PROPERTIES_PORT);
            LogonUsername = GetAccountProp(LogOnAccount, PROPERTIES_USERNAME);
            ReconcileUsername = GetAccountProp(ReconcileAccount, PROPERTIES_USERNAME);
            CurrentPassword = GetAccountPassword(TargetAccount);
            LogonCurrentPassword = GetAccountPassword(LogOnAccount);
            ReconcileCurrentPassword = GetAccountPassword(ReconcileAccount);
            NewPassword = GetNewPassword();
            LogField(nameof(Username), Username);
            LogField(nameof(Address), Address);
            LogField(nameof(Port), Port);
            LogField(nameof(LogonUsername), LogonUsername);
            LogField(nameof(ReconcileUsername), ReconcileUsername);
            LogField(nameof(CurrentPassword), CurrentPassword);
            LogField(nameof(LogonCurrentPassword), LogonCurrentPassword);
            LogField(nameof(ReconcileCurrentPassword), ReconcileCurrentPassword);
            LogField(nameof(NewPassword), NewPassword);
        }

        private Dictionary<string, string> GetArgs(string action)
        {
            return new Dictionary<string, string>
            {
                { ENV_ACTION, action },
                { ENV_USERNAME, Username },
                { ENV_ADDRESS, Address },
                { ENV_PORT, Port },
                { ENV_LOGON_USERNAME, LogonUsername },
                { ENV_RECONCILE_USERNAME, ReconcileUsername },
                { ENV_LOGGING, PythonLogging },
                { ENV_LOGGING_LEVEL, PythonLoggingLevel }
            };
        }

        private Dictionary<string, EncryptedString> GetSecrets()
        {
            return new Dictionary<string, EncryptedString>
            {
                { ENV_PASSWORD, CurrentPassword },
                { ENV_LOGON_PASSWORD, LogonCurrentPassword },
                { ENV_RECONCILE_PASSWORD, ReconcileCurrentPassword },
                { ENV_NEW_PASSWORD, NewPassword }
            };
        }

        private void RunScript(string action)
        {
            var args = GetArgs(action);
            var secrets = GetSecrets();
            var process = new Process
            {
                StartInfo = new ProcessStartInfo
                {
                    FileName = PythonExePath,
                    Arguments = $"\"{PythonScriptPath}\"",
                    UseShellExecute = false,
                    RedirectStandardInput = false,
                    RedirectStandardOutput = false,
                    RedirectStandardError = true,
                    CreateNoWindow = true
                }
            };
            foreach (var arg in args)
            {
                LogEnvVar(arg.Key, arg.Value);
                process.StartInfo.EnvironmentVariables[arg.Key] = arg.Value;
            }
            foreach (var secret in secrets)
            {
                LogEnvVar(secret.Key, secret.Value);
                process.StartInfo.EnvironmentVariables[secret.Key] = secret.Value.Secret;
            }
            Logger.WriteLine($"Executing: {PythonExePath} {PythonScriptPath}", LogLevel.INFO);
            process.Start();
            string stderr = process.StandardError.ReadToEnd();
            process.WaitForExit();
            string message = $"Python closed with exit code: {process.ExitCode}";
            if (process.ExitCode != PYTHON_CLOSE_SUCCESS)
            {
                Logger.WriteLine(message, LogLevel.ERROR);
                if (!string.IsNullOrWhiteSpace(stderr))
                {
                    Logger.WriteLine($"StdErr Output: {stderr}", LogLevel.ERROR);
                }
                throw new PythonExecutionException(process.ExitCode);
            }
            Logger.WriteLine(message, LogLevel.INFO);
        }

        protected int RunAction(string action, ref PlatformOutput platformOutput)
        {
            try
            {
                GetParams();
                GetAccountData();
            }
            catch (Exception ex)
            {
                return HandleException(ex, true, ref platformOutput);
            }
            try
            {
                RunScript(action);
                Logger.WriteLine("Closing with success", LogLevel.INFO);
                return CLOSE_SUCCESS;
            }
            catch (PythonExecutionException ex)
            {
                if (ex.ExitCode == PYTHON_CLOSE_FAILED_RECOVERABLE)
                {
                    return HandleException(ex, false, ref platformOutput);
                }
                return HandleException(ex, true, ref platformOutput);
            }
            catch (Exception ex)
            {
                return HandleException(ex, true, ref platformOutput);
            }
        }

        private int HandleException(Exception ex, bool unrecoverable, ref PlatformOutput platformOutput)
        {
            platformOutput.Message = ex.Message;
            Logger.WriteLine($"{ex.GetType()}: {ex.Message}", LogLevel.ERROR);
            if (unrecoverable)
            {
                Logger.WriteLine("Closing with failed unrecoverable", LogLevel.ERROR);
                return CLOSE_FAILED_UNRECOVERABLE;
            }
            Logger.WriteLine("Closing with failed recoverable", LogLevel.ERROR);
            return CLOSE_FAILED_RECOVERABLE;
        }
    }
}
