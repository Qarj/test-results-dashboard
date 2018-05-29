using System;

namespace Prime.Services
{
    public class PrimeService
    {
        public bool IsPrime(int candidate)
        {
            if (candidate <= 1) return false;
            else if (candidate <= 3) return true;
            else if ( (candidate % 2 == 0) || (candidate % 3 == 0) ) return false;
            var i = 5;
            while (i * i <= candidate)
            {
                if ( (candidate % i == 0) || (candidate % (i + 2) == 0) )
                    return false;
                i = i + 6;
            }
            return true;
        }

        public bool IsException(int candidate)
        {
            throw new NotImplementedException("We need a test please");
        }
    }
}