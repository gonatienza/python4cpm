using System;

namespace CyberArk.Extensions.Python4CPM
{
    public class PythonExecutionException : Exception
    {
        public int ExitCode { get; }

        public PythonExecutionException(string message, int exitCode) : base(message)
        {
            ExitCode = exitCode;
        }
    }
}
