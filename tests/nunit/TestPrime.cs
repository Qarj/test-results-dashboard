using NUnit.Framework;
using Prime.Services;
using System;
using System.Linq;
using System.IO;
using System.Net;
using System.Text.RegularExpressions;

namespace Prime.UnitTests.Services
{
    [TestFixture]
    public class TestPrime
    {
        private readonly PrimeService _primeService;
        
        private string runName;
        private string runServer;
        private string appName = "PrimeService";
        
        [OneTimeSetUp]
        protected void OneTimeSetUp()
        {
            runName = Dashboard.RandomString(5);
            runServer = Dashboard.RunServer();
        }
        
        [SetUp]
        protected void SetUp()
        {
            Console.WriteLine("Welcome to the set up!");
            string result = Dashboard.LogResult(Dashboard.GetTestName(), appName, runName, runServer, "Pending");
        }

        [TearDown]
        protected void TearDown()
        {
            string testName = Dashboard.GetTestName();
            string testStatus = Dashboard.GetTestStatus();
            string result = Dashboard.LogResult(testName, appName, runName, runServer, testStatus);
            //Console.WriteLine(testStatus);
            //Console.WriteLine("Log Result Message: " + result );
        }

        public TestPrime()
        {
            _primeService = new PrimeService();
        }

        [Test]
        public void ReturnFalseGivenValueOf1()
        {
            Console.WriteLine("run_name[" + runName + "] run_server[" + runServer + "]");
            var result = _primeService.IsPrime(1);

            Assert.IsFalse(result, "1 should not be prime");
        }

        [Test]
        public void ReturnTrueGivenValueOf2()
        {
            Console.WriteLine("run_name[" + runName + "] run_server[" + runServer + "]");
            var result = _primeService.IsPrime(2);

            Assert.IsTrue(result, "2 truly is a prime");
        }

        [Test]
        public void ReturnTrueGivenValueOf42()
        {
            var result = _primeService.IsPrime(42);

            Assert.IsTrue(result, "42 should be a prime, or?");
        }

        [Test]
        public void PleaseDontExcept()
        {
            var result = _primeService.IsException(42);

            Assert.IsTrue(result, "42 is an exception to the rule");
        }

        [Test]
        [Ignore("Ignore this test")]
        public void IgnoreThisBadlyWrittenTest()
        {
            var result = _primeService.IsPrime(23/10);

            Assert.IsTrue(result, "2.3 is sort of Prime");
        }

    }

    public static class Dashboard
    {

        private static Random random = new Random();
        public static string RandomString(int length)
        {
            const string chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789";
            return new string(Enumerable.Repeat(chars, length)
              .Select(s => s[random.Next(s.Length)]).ToArray());
        }
        
        public static string RunServer()
        {
            return Environment.GetEnvironmentVariable("computername");
        }
        
        public static string LogResult(string testName, string appName, string runName, string runServer, string testStatus)
        {
            string logURL = "http://dash/dash/results/log?";
            string queryString = String.Format("test_name={0}&app_name={1}&run_name={2}&run_server={3}&test_passed={4}",
                                     testName, appName, runName, runServer, testStatus);
            //Console.WriteLine("Log URL: " + logURL + queryString );

            try
            {
                return Get(logURL + queryString);
            }
            catch (WebException e)
            {
                return "Web request failed";
            }
        }

        private static string Get(string uri)
        {
            HttpWebRequest request = (HttpWebRequest)WebRequest.Create(uri);
            request.AutomaticDecompression = DecompressionMethods.GZip | DecompressionMethods.Deflate;

            using(HttpWebResponse response = (HttpWebResponse)request.GetResponse())
            using(Stream stream = response.GetResponseStream())
            using(StreamReader reader = new StreamReader(stream))
            {
                return reader.ReadToEnd();
            }
        }
        
        public static string GetTestName()
        {
            return Dashboard._LastTwoSegmentsOfNUnitTestFullName(NUnit.Framework.TestContext.CurrentContext.Test.FullName);
        }

        private static string _LastTwoSegmentsOfNUnitTestFullName(string testName)
        {
            string[] segments = Regex.Split(testName, "\\.");
            return segments[segments.Length - 2] + "." + segments.Last();
        }

        public static string GetTestStatus()
        {
            return NUnit.Framework.TestContext.CurrentContext.Result.Outcome.Status.ToString();
        }

    }

}