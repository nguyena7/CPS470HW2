# networkHop.py
import const
import tweepy
import sys
from collections import defaultdict

# # # Graph Class for printing # # #
class Graph:
    def __init__(self):
        self.graph = defaultdict(list)

    def add_edge(self, user, friend):
        self.graph[user].append(friend)

    def print_graph(self):
        print("---------- Printing the all users and their friends ----------")
        for key, value in self.graph.items():
            print("name: %s" % key.screen_name)
            for friend_node in value:
                print("---%s" % friend_node.screen_name)

# # # Node Class used to wrap the Tweepy 'User' Object (The 'User' Object was unhashable in the set) # # #
class Node:
    def __init__(self, user):
        self.user = user
        self.id = user.id
        self.screen_name = user.screen_name
        self.friend_count = user.friends_count
        self.follower_count = user.followers_count

# # # Sort the items in the set by friends/followers count # # #
def sort_set(friends_list):
    sorted_by_friends = sorted(friends_list, key=sort_node_friends)
    sorted_by_followers = sorted(friends_list, key=sort_node_followers)
    return sorted_by_followers, sorted_by_friends

# # # key used by sorted() to sort by Node.friend_count # # #
def sort_node_friends(node):
    return node.friend_count

# # # key used by sorted() to sort by Node.follower_count # # #
def sort_node_followers(node):
    return node.follower_count

# # # Print the Final results from the sets # # #
def print_set(sorted_by_followers, sorted_by_friends): # # # sorted_set: set sorted by friends or followers
    print("\n------------ FINAL RESULTS ------------")
    print("The sorted set of friends sorted by FOLLOWER COUNT are:")
    counter = 1
    for friends in sorted_by_followers[:10]:
        print("%d. %s w/ %d followers" % (counter, friends.screen_name, friends.follower_count))
        counter += 1

    counter = 1
    print("The sorted set of friends sorted by FRIEND COUNT are:")
    for friends in sorted_by_friends[:10]:
        print("%d. %s w/ %d friends" % (counter, friends.screen_name, friends.friend_count))
        counter += 1

# # # BFS Function # # #
def BFS(api, friend_amount, hops):
    graph = Graph()
    queue = [] # #  BSF queue
    friends_list = set()  # # Store All Friend objects (of Node object)
    names_visited = set()  # # Store all User.screen_name (Twitter 'User' object was unhashable)

    user_name = 'univofdayton'
    user = api.get_user(screen_name=user_name)
    user_node = Node(user)
    queue.append(user_node)
    friends_list.add(user_node)

    # # # Set the amount of 'friend' nodes to visit per 'parent' node
    num_friends_wanted = friend_amount

    # # # Hop loop
    for hop in range(0, hops):
        print(" - - - - - HOP: %d - - - - -\n" % (hop + 1))
        queue_counter = 0

        # # # BFS Loop
        while queue:
            # # # Number of people to remove from the queue per hop
            friends_in_current_hop = num_friends_wanted ** hop

            # # # If number of friends popped from queue per hop is reached
            if queue_counter == friends_in_current_hop:
                break

            queue_counter += 1
            user_node = queue.pop(0)

            # # # Counter to indicate how many friends where found
            friend_counter = 0
            try:
                for friend in tweepy.Cursor(api.friends, screen_name=user_node.screen_name).items():
                    # # # If the amount of friends found is equal to how many friends we wanted
                    if friend_counter == num_friends_wanted:
                        break

                    friendship = api.show_friendship(source_screen_name=user.screen_name, target_screen_name=friend.screen_name)
                    friend_node = Node(friend)

                    # # # Find out if both users are following each other
                    if friendship[0].following is True and friendship[1].following is True:
                        print("Current Node, %s has friend: %s\n" % (user_node.screen_name, friend_node.screen_name))
                        if friend.screen_name not in names_visited:
                            friend_counter += 1
                            queue.append(friend_node)
                            names_visited.add(friend.screen_name)
                            friends_list.add(friend_node)
                            graph.add_edge(user_node, friend_node)
                        else:
                            print("* * * Friend %s was already visited\n" % friend_node.screen_name)
            except tweepy.TweepError:
                print("Could not access account, maybe protected account?")

    return graph, friends_list

def main():
    auth = tweepy.OAuthHandler(const.CONSUMER_KEY, const.CONSUMER_SECRET)
    auth.set_access_token(const.ACCESS_TOKEN, const.ACCESS_TOKEN_SECRET)
    api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True, retry_errors=([503]))

    if len(sys.argv)-1 == 0:
        print("Invalid command line arguments")
        print("Usage: %s [friends to search per User] [hop amount]" % sys.argv[0])
        return

    try:
        friend_amount = int(sys.argv[1])
        hops = int(sys.argv[2])
    except ValueError:
        print("Invalid command line arguments")
        print("Usage: %s [friends to search per User] [hop amount]" % sys.argv[0])
        return

    graph, friends_list = BFS(api, friend_amount, hops)

    graph.print_graph()

    sorted_by_friends, sorted_by_followers = sort_set(friends_list)

    print_set(sorted_by_friends, sorted_by_followers)

# call main method
if __name__ == "__main__":
    main()
