using System;

namespace CyberArk.Extensions.Plugin.Python4CPM
{
    public class PythonExecutionException : Exception
    {
        public int ExitCode { get; }

        public override string Message
        {
            get
            {
                switch (ExitCode)
                {
                    case BaseAction.PYTHON_CLOSE_FAILED_UNRECOVERABLE:
                        return "Python closed with failed unrecoverable";
                    case BaseAction.PYTHON_CLOSE_FAILED_RECOVERABLE:
                        return "Python closed with failed recoverable";
                    default:
                        return "Python closed unexpectedly";
                }
            }
        }

        public PythonExecutionException(int exitCode) : base()
        {
            ExitCode = exitCode;
        }
    }
}
