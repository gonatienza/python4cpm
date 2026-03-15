using CyberArk.Extensions.Plugins.Models;
using CyberArk.Extensions.Utilties.Logger;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System;

namespace CyberArk.Extensions.Plugin.Python4CPM
{
    abstract public class BaseAction : AbsAction
    {
        private const string ParamsPythonExePath = "PythonExePath";
        private const string ParamsPythonScriptPath = "PythonScriptPath";
        private const string ParamsPythonLoggingLevel = "PythonLoggingLevel";
        private const string PropertiesPolicyId = "policyid";
        private const string PropertiesObjectName = "objectname";
        private const string PropertiesUsername = "username";
        private const string PropertiesAddress = "address";
        private const string PropertiesPort = "port";
        private const int CloseSuccess = 0;
        private const int CloseFailedUnrecoverable = 8900;
        private const int CloseFailedRecoverable = 8100;
        private const int PythonCloseSuccess = 10;
        public const int PythonCloseFailedUnrecoverable = 89;
        public const int PythonCloseFailedRecoverable = 81;
        private string PythonExePath;
        private string PythonScriptPath;
        private string PythonLoggingLevel;
        private string TargetPolicyId;
        private string TargetObjectName;
        private string TargetUsername;
        private string TargetAddress;
        private string TargetPort;
        private string LogonUsername;
        private string ReconcileUsername;
        private EncryptedString TargetCurrentPassword;
        private EncryptedString LogonCurrentPassword;
        private EncryptedString ReconcileCurrentPassword;
        private EncryptedString TargetNewPassword;

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
            if (obj == null)
                return $"[NOT SET]";
            if (obj is EncryptedString)
                return $"{obj}";
            return $"'{obj}'";
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

        private void GetParams()
        {
            if (TargetAccount?.ExtraInfoProp?.ContainsKey(ParamsPythonExePath) == true)
                PythonExePath = TargetAccount.ExtraInfoProp[ParamsPythonExePath];
            if (TargetAccount?.ExtraInfoProp?.ContainsKey(ParamsPythonScriptPath) == true)
                PythonScriptPath = TargetAccount.ExtraInfoProp[ParamsPythonScriptPath];
            if (TargetAccount?.ExtraInfoProp?.ContainsKey(ParamsPythonLoggingLevel) == true)
                PythonLoggingLevel = TargetAccount.ExtraInfoProp[ParamsPythonLoggingLevel];
            LogField(nameof(PythonExePath), PythonExePath);
            LogField(nameof(PythonScriptPath), PythonScriptPath);
            LogField(nameof(PythonLoggingLevel), PythonLoggingLevel);
            if (!File.Exists(PythonExePath))
                throw new FileNotFoundException($"{ParamsPythonExePath}: '{PythonExePath}' not found");
            if (!File.Exists(PythonScriptPath))
                throw new FileNotFoundException($"{ParamsPythonScriptPath}: '{PythonScriptPath}' not found");
        }

        private void GetAccounts()
        {
            if (TargetAccount?.AccountProp?.ContainsKey(PropertiesPolicyId) == true)
                TargetPolicyId = TargetAccount.AccountProp[PropertiesPolicyId];
            if (TargetAccount?.AccountProp?.ContainsKey(PropertiesObjectName) == true)
                TargetObjectName = TargetAccount.AccountProp[PropertiesObjectName];
            if (TargetAccount?.AccountProp?.ContainsKey(PropertiesUsername) == true)
                TargetUsername = TargetAccount.AccountProp[PropertiesUsername];
            if (TargetAccount?.AccountProp?.ContainsKey(PropertiesAddress) == true)
                TargetAddress = TargetAccount.AccountProp[PropertiesAddress];
            if (TargetAccount?.AccountProp?.ContainsKey(PropertiesPort) == true)
                TargetPort = TargetAccount.AccountProp[PropertiesPort];
            if (LogOnAccount?.AccountProp?.ContainsKey(PropertiesUsername) == true)
                LogonUsername = LogOnAccount.AccountProp[PropertiesUsername];
            if (ReconcileAccount?.AccountProp?.ContainsKey(PropertiesUsername) == true)
                ReconcileUsername = ReconcileAccount.AccountProp[PropertiesUsername];
            if (TargetAccount?.CurrentPassword?.Length > 0)
                TargetCurrentPassword = Crypto.Encrypt(TargetAccount.CurrentPassword);
            if (LogOnAccount?.CurrentPassword?.Length > 0)
                LogonCurrentPassword = Crypto.Encrypt(LogOnAccount.CurrentPassword);
            if (ReconcileAccount?.CurrentPassword?.Length > 0)
                ReconcileCurrentPassword = Crypto.Encrypt(ReconcileAccount.CurrentPassword);
            if (RequiresNewPassword && TargetAccount?.NewPassword?.Length > 0)
                TargetNewPassword = Crypto.Encrypt(TargetAccount.NewPassword);
            LogField(nameof(TargetPolicyId), TargetPolicyId);
            LogField(nameof(TargetObjectName), TargetObjectName);
            LogField(nameof(TargetUsername), TargetUsername);
            LogField(nameof(TargetAddress), TargetAddress);
            LogField(nameof(TargetPort), TargetPort);
            LogField(nameof(LogonUsername), LogonUsername);
            LogField(nameof(ReconcileUsername), ReconcileUsername);
            LogField(nameof(TargetCurrentPassword), TargetCurrentPassword);
            LogField(nameof(LogonCurrentPassword), LogonCurrentPassword);
            LogField(nameof(ReconcileCurrentPassword), ReconcileCurrentPassword);
            LogField(nameof(TargetNewPassword), TargetNewPassword);
        }

        private void RunScript(string action)
        {
            var args = EnvHandler.GetArgs(
                action,
                TargetPolicyId,
                TargetObjectName,
                TargetUsername,
                TargetAddress,
                TargetPort,
                LogonUsername,
                ReconcileUsername,
                PythonLoggingLevel);
            var secrets = EnvHandler.GetSecrets(
                TargetCurrentPassword,
                LogonCurrentPassword,
                ReconcileCurrentPassword,
                TargetNewPassword);
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
                process.StartInfo.EnvironmentVariables[secret.Key] = secret.Value.Value;
            }
            Logger.WriteLine($"Executing: {PythonExePath} {PythonScriptPath}", LogLevel.INFO);
            process.Start();
            string stderr = process.StandardError.ReadToEnd();
            process.WaitForExit();
            string message = $"Python closed with exit code: {process.ExitCode}";
            if (process.ExitCode != PythonCloseSuccess)
            {
                Logger.WriteLine(message, LogLevel.ERROR);
                if (!string.IsNullOrWhiteSpace(stderr))
                    Logger.WriteLine($"StdErr Output: {stderr}", LogLevel.ERROR);
                throw new PythonExecutionException(process.ExitCode);
            }
            Logger.WriteLine(message, LogLevel.INFO);
        }

        protected int RunAction(string action, ref PlatformOutput platformOutput)
        {
            Logger.WriteLine($"Running action: {action}", LogLevel.INFO);
            try
            {
                GetParams();
                GetAccounts();
            }
            catch (Exception ex)
            {
                return HandleException(ex, true, ref platformOutput);
            }
            try
            {
                RunScript(action);
                Logger.WriteLine("Closing with success", LogLevel.INFO);
                return CloseSuccess;
            }
            catch (PythonExecutionException ex)
            {
                if (ex.ExitCode == PythonCloseFailedRecoverable)
                    return HandleException(ex, false, ref platformOutput);
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
                return CloseFailedUnrecoverable;
            }
            Logger.WriteLine("Closing with failed recoverable", LogLevel.ERROR);
            return CloseFailedRecoverable;
        }
    }
}
