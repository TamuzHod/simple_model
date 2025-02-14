# Simple Model API

[Previous content up to GraphQL Features section...]

### Sample GraphQL Queries

Here are some example queries you can use in the GraphQL Playground:

```graphql
# Get a list of users with basic information
query GetUsers {
  users(first: 20) {
    edges {
      node {
        uuid
        name
        email
        isActive
      }
    }
    totalCount
  }
}

# Get a specific user and their friends
query GetUserWithFriends {
  user(uuid: "67afa2945d9579aa178f23d7") {
    name
    email
    friends {
      edges {
        node {
          name
          email
        }
      }
    }
  }
}

# Get a user with their referral information
query GetUserWithReferrals {
  user(uuid: "67afa2945d9579aa178f23d7") {
    name
    referredUsers {
      edges {
        node {
          name
          email
        }
      }
    }
    referrer {
      name
      email
    }
  }
}

# Get users with pagination information
query UsersWithFriends($pageSize: Int = 15) {
  users(first: $pageSize) {
    edges {
      node {
        uuid
        email
        name
        isActive
        createdAt
        updatedAt
        referredBy
      }
    }
    pageInfo {
      hasNextPage
      hasPreviousPage
      startCursor
      endCursor
    }
    totalCount
  }
}

# Get users with both friends and referrals
query UsersWithFriendsAndRefferals($pageSize: Int = 15) {
  users(first: $pageSize) {
    edges {
      node {
        uuid
        email
        name
        isActive
        createdAt
        updatedAt
        referredBy
        referredUsers(first: 10) {
          edges {
            node {
              name
            }
          }
          totalCount
        }
        friends(first: 10) {
          edges {
            node {
              name
            }
          }
          totalCount
        }
      }
    }
    pageInfo {
      hasNextPage
      hasPreviousPage
      startCursor
      endCursor
    }
    totalCount
  }
}
```

[Rest of the original content...]
