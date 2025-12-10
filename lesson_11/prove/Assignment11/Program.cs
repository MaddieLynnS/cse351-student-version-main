using System.Collections;
using System.Diagnostics;

namespace assignment11;

public class Assignment11
{
    private const long START_NUMBER = 10_000_000_000;
    private const int RANGE_COUNT = 1_000_000;
    private const int WORKER_NUM = 10;

    private static int _numbersProcessed;
    private static int _primeCount;
    private static readonly object _queueLock = new object();


    private static bool IsPrime(long n)
    {
        if (n <= 3) return n > 1;
        if (n % 2 == 0 || n % 3 == 0) return false;

        for (long i = 5; i * i <= n; i = i + 6)
        {
            if (n % i == 0 || n % (i + 2) == 0)
                return false;
        }
        return true;
    }

    private static void Worker(Queue<long> numberQueue)
    {
        while (true)
        {
            long currentNum;
            lock (_queueLock)
            {
                if (numberQueue.Count == 0)
                {
                    return;
                }

                currentNum = numberQueue.Dequeue();
            }

            Interlocked.Increment(ref _numbersProcessed);
            if (IsPrime(currentNum))
            {
                Interlocked.Increment(ref _primeCount);
                Console.Write($"{currentNum}, ");
            }
        }

    }

    public static void Main(string[] args)
    {
        // creating queue and threads
        Queue<long> numberQueue = new Queue<long>();
        List<Thread> threads = new List<Thread>();


        Console.WriteLine("Prime numbers found:");

        var stopwatch = Stopwatch.StartNew();
        
        // A single for-loop to add numbers to a queue
        for (long i = START_NUMBER; i < START_NUMBER + RANGE_COUNT; i++)
        {
            numberQueue.Enqueue(i);
        }
        
        // start threads based on number of specified workers
        for (int i = 0; i < WORKER_NUM; i++)
        {
            Thread newThread = new Thread(() => Worker(numberQueue));
            threads.Add(newThread);
            
            newThread.Start();
        }

        foreach (var t in threads)
        {
            t.Join();
        }

        stopwatch.Stop();

        Console.WriteLine(); // New line after all primes are printed
        Console.WriteLine();

        // Should find 43427 primes for range_count = 1000000
        Console.WriteLine($"Numbers processed = {_numbersProcessed}");
        Console.WriteLine($"Primes found      = {_primeCount}");
        Console.WriteLine($"Total time        = {stopwatch.Elapsed}");        
    }
}