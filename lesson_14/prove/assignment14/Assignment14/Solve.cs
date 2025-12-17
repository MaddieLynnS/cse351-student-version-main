using System.Collections.Concurrent;
using Newtonsoft.Json.Linq;

namespace Assignment14;

public static class Solve
{
    private static readonly object TreeLock = new object();
    
    private static readonly HttpClient HttpClient = new()
    {
        Timeout = TimeSpan.FromSeconds(180)
    };
    public const string TopApiUrl = "http://127.0.0.1:8123";

    // This function retrieves JSON from the server
    public static async Task<JObject?> GetDataFromServerAsync(string url)
    {
        try
        {
            var jsonString = await HttpClient.GetStringAsync(url);
            return JObject.Parse(jsonString);
        }
        catch (HttpRequestException e)
        {
            //Console.WriteLine($"Error fetching data from {url}: {e.Message}");
            return null;
        }
    }

    // This function takes in a person ID and retrieves a Person object
    // Hint: It can be used in a "new List<Task<Person?>>()" list
    private static async Task<Person?> FetchPersonAsync(long personId)
    {
        var personJson = await Solve.GetDataFromServerAsync($"{Solve.TopApiUrl}/person/{personId}");
        return personJson != null ? Person.FromJson(personJson.ToString()) : null;
    }

    // This function takes in a family ID and retrieves a Family object
    // Hint: It can be used in a "new List<Task<Family?>>()" list
    private static async Task<Family?> FetchFamilyAsync(long familyId)
    {
        var familyJson = await Solve.GetDataFromServerAsync($"{Solve.TopApiUrl}/family/{familyId}");
        return familyJson != null ? Family.FromJson(familyJson.ToString()) : null;
    }
    
    // =======================================================================================================
    public static async Task<bool> DepthFS(long familyId, Tree tree)
    {
        var familyFetch = FetchFamilyAsync(familyId);
        Family? family = await familyFetch;
        if (family == null)
        {
            //Console.WriteLine("No family found");
            return false;
        }
        
        //Console.WriteLine("Found family");
        //Console.WriteLine(family);
        lock (TreeLock)
        {
            tree.AddFamily(family);
        }

        //Find parents, make in Person objects, and add to the tree
        Person? husband = await FetchPersonAsync(family.HusbandId);
        Person? wife = await FetchPersonAsync(family.WifeId);

        lock (TreeLock)
        {
            tree.AddPerson(husband);
            tree.AddPerson(wife);
        }

        Task t = Task.Run(() => DepthFS(husband.ParentId, tree));
        Task wt = Task.Run(() => DepthFS(wife.ParentId, tree));

        foreach (long childId in family.Children)
        {
            //if child doesn't exist yet, get them and add them to the tree
            if (!tree.PersonExists(childId))
            {
                Person? child = await FetchPersonAsync(childId);
                lock (TreeLock)
                {
                    tree.AddPerson(child);
                }
            }
        }

        t.Wait();
        wt.Wait();

        //Console.WriteLine("All done!");
        return true;
    }

    // =======================================================================================================
    public static async Task<bool> BreadthFS(long famid, Tree tree)
    {
        // Note: invalid IDs are zero not null
        //Queue to hold ids that is thread-safe I think?
        ConcurrentQueue<long> queue = new ConcurrentQueue<long>();
        queue.Enqueue(famid);

        const int workers = 50;
        List<Task> tasks = new List<Task>();
        for (int i = 0; i < workers; i++)
        {
            Task t = Task.Run(() => CallAPIWorker(tree, queue));
            tasks.Add(t);
        }

        await Task.WhenAll(tasks);
        
        return true;
    }

    private static async Task CallAPIWorker(Tree tree, ConcurrentQueue<long> queue)
    {
        while (true)
        {
            bool worked = queue.TryDequeue(out long nextId);
            if (nextId == -1)
            {
                break;
            }

            if (!worked)
            {
                await Task.Delay(5);
                continue;
            }
            
            var familyFetch = FetchFamilyAsync(nextId);
            Family? family = await familyFetch;
            if (family == null)
            {
                //Console.WriteLine("No family found lol");
                queue.Enqueue(-1);
                continue;
            }
            
            //Console.WriteLine("Found family");
            //Console.WriteLine(family);
            lock (TreeLock)
            {
                tree.AddFamily(family);
            }
            
            //Find parents, make in Person objects, and add to the tree
            Person? husband = await FetchPersonAsync(family.HusbandId);
            Person? wife = await FetchPersonAsync(family.WifeId);

            lock (TreeLock)
            {
                tree.AddPerson(husband);
                tree.AddPerson(wife);
            }
            
            //Add next ids to the queue
            queue.Enqueue(husband.ParentId);
            queue.Enqueue(wife.ParentId);
            
            //Add children to tree as well
            foreach (long childId in family.Children)
            {
                //if child doesn't exist yet, get them and add them to the tree
                if (!tree.PersonExists(childId))
                {
                    Person? child = await FetchPersonAsync(childId);
                    lock (TreeLock)
                    {
                        tree.AddPerson(child);
                    }
                }
            }
        }
        //Console.WriteLine("HEY IM ENQUEUEING A -1");
        //If it broke, then enqueue another -1
        queue.Enqueue(-1);
    }
    //Code from python version of this nonsense
//     
//     def breadth_fs_pedigree(family_id, tree:Tree):
//     # uses start id and like starts with the family, puts it in the queue, then gets individuals and puts them in the queue too
//     
//     #initialize queue and lock, and add first family id
//     processing_queue = queue.Queue()
//     add_to_tree = threading.Lock()
//     processing_queue.put(family_id)
//
//     threads = []
//     for _ in range(THREADS):
//         t = threading.Thread(target=call_API_worker, args=(tree, add_to_tree, processing_queue))
//         t.start()
//         threads.append(t)
//
//     # Chat tried to tell me this was the way to do it and I said no, this is wrong, cuz we're continuously adding to the queue
//     # for _ in range(THREADS):
//     #     processing_queue.put(None)
//
//     for t in threads:
//         t.join()
//
//
// # this function gets a family, gets the husband and wife and puts their parent ids in the queue, then processes and add children
// # each thread takes care of the next API call, like worker threads
// def call_API_worker(tree:Tree, add_to_tree: threading.Lock, process_queue : queue.Queue):
//     while True:
//         next_id = process_queue.get()
//         if next_id is None:
//             break
//         
//         #get data from API to process
//         data = get_data_from_server(f'{TOP_API_URL}/family/{next_id}')
//         # print(f"Here is the data: {data}")
//         if (data is None):
//             continue
//         
//         family = Family(data)
//         #print(family)
//         with add_to_tree:
//             tree.add_family(family)
//
//         # use ids to get husband and wife, then get their data from API
//         husband_id = family.get_husband()
//         wife_id = family.get_wife()
//
//         husband_data = get_data_from_server(f'{TOP_API_URL}/person/{husband_id}')
//         wife_data = get_data_from_server(f'{TOP_API_URL}/person/{wife_id}')
//
//         # make them both people and add them to the tree
//         husband = Person(husband_data)
//         wife = Person(wife_data)
//         with add_to_tree:
//             tree.add_person(husband)
//             tree.add_person(wife)
//
//         #Add the next families to be processed into the tree
//         process_queue.put(husband.get_parentid())
//         process_queue.put(wife.get_parentid())
//
//         for i in family.get_children():
//             if not tree.does_person_exist(i):
//                 child = Person(get_data_from_server(f'{TOP_API_URL}/person/{i}'))
//                 with add_to_tree:
//                     tree.add_person(child)
//
//     # if the loop breaks, that means we can put a None back in the queue and be done with this thread
//     process_queue.put(None)
}
