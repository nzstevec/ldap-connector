from ldap3 import Server, Connection, ALL, ALL_ATTRIBUTES, SUBTREE

# a rest api to connect to ldap server and query for user details and groups details 
 
def main():
    #  connect to ldap server and bind to it 
    host = 'ldap://eqa-uat-dir.nzqa.govt.nz'
    port = 389
    user = 'cn=admin,o=nzqa'
    pw = 'password'
    conn = connectToLdap(host,port,user,pw)
    # print(conn)
    # get list of users
    # userId = input("enter userId : ")
    userId = "nzqaTPE174"
    userEntries = getUserEntries(conn,base='ou=Users2,o=dev',userId=userId)
    #  query for user details
    for entry in userEntries:
        # display uid if it exists only
        # print(f"dn: {entry.entry_dn}\n  - uid: {entry.uid if entry.uid else 'None'}") 
        # print(f"  - groupMembership: {entry.groupMembership if entry.groupMembership else 'None'}")
        userRoleDns = getRoleDns(conn,base=entry.entry_dn)
        userRoles = []
        for role in userRoleDns:
            print(f"roleDn: {role['dn']}",end='')
            userRole = getRole(conn,base=role['dn'])
            print(f", role {userRole[0]['dn']}")
            userRoles.append(userRole[0]['dn'])
        
    #  return the results 
    # displayResults()
    
def connectToLdap(host,port,user,pw) -> Connection : 
    #  connect to ldap server and bind to it 
    ldapServer = Server(host=host, port=port, get_info=ALL)
    ldapConn = Connection(ldapServer, user=user, password=pw, auto_bind=True)
    # print("Connected to ldap server")
    # print(ldapServer.info)
    # print("------------------------------")
    # print("schema info")
    # print(ldapServer.schema)
    # print("------------------------------")
    return ldapConn

def getUserEntries(conn,base,userId) -> list : 
    #  query for user details
    conn.search(search_base=base, 
                # search_filter='(&(objectClass=Person)(groupMembership=*))', 
                # search_filter='(&(objectclass=eqaUser)(uid={0}*))',
                search_filter=f'(sia-userid={userId})',
                search_scope=SUBTREE, attributes=ALL_ATTRIBUTES)
    print(f"User search returned {len(conn.entries)} entries")
    # print("User List")
    # print(conn.entries)
    return conn.entries

def getListOfUsers(conn,base) -> list : 
    #  query for user details
    conn.search(search_base=base, 
                # search_filter='(&(objectClass=Person)(groupMembership=*))', 
                # search_filter='(&(objectclass=eqaUser)(uid={0}*))',
                search_filter='(sia-userid=*)',
                attributes=['groupMembership','uid','securityEquals'])
    print(f"User search returned {len(conn.entries)} entries")
    # print("User List")
    # print(conn.entries)
    return conn.entries

def getRoleDns(conn,base) -> dict : 
    #  query for user details
    conn.search(search_base=base, 
                search_filter='(objectClass=eqaContext2)', 
                search_scope=SUBTREE, attributes=ALL_ATTRIBUTES)
    # print("User Role Dns")
    print(conn.response)
    return conn.response

def getRole(conn,base) -> dict : 
    #  query for user details
    conn.search(search_base=base, 
                search_filter='(objectClass=eqaRoleAssociation2)', 
                search_scope=SUBTREE, attributes=ALL_ATTRIBUTES)
    # print("User Role")
    print(conn.response)
    return conn.response

def getGroupsDetails(conn,username,base):
    #  query for groups details
    conn.search(search_base=base, 
                search_filter='(cn='+username+')', 
                attributes=['cn','sn','givenName','fullName','ou','o'])
    print("Groups Details")
    print(conn.response)
    return conn.response

def getRolesDetails(conn,username,base):
    #  query for roles details
    conn.search(search_base=base, 
                search_filter='(cn='+username+')', 
                # all attributes 
                attributes=['cn','sn','givenName','fullName','ou','o'])
    print("Roles Details")
    print(conn.response)
    return conn.response

if __name__ == '__main__':
    main()