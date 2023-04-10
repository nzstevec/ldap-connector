from ldap3 import Server, Connection, ALL

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
    userEntries = getListOfUsers(conn,base='ou=Users2,o=dev')
    #  query for user details
    # users = ['tertop1','testeqa1','web_appserver_secure']
    for entry in userEntries:
        # display uid if it exists only
        print(f"dn: {entry.entry_dn}\n  - uid: {entry.uid if entry.uid else 'None'}") 
        print(f"  - groupMembership: {entry.groupMembership if entry.groupMembership else 'None'}")
        # getUserDetails(conn,username=name,base='ou=Users,o=dev')
        #  query for groups details
        # getGroupsDetails(conn,username=username,base='ou=Groups,o=dev')
        # query roles details
        # getRolesDetails(conn,username=username,base='ou=Roles,o=dev')
        
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

def getListOfUsers(conn,base) -> list : 
    #  query for user details
    conn.search(search_base=base, 
                search_filter='(&(objectClass=Person)(groupMembership=*))', 
                # search_filter='(&(objectclass=eqaUser)(uid={0}*))',
                attributes=['groupMembership','uid','securityEquals'])
    print(f"User search returned {len(conn.entries)} entries")
    # print("User List")
    # print(conn.entries)
    return conn.entries

def getUserDetails(conn,username,base) -> dict : 
    #  query for user details
    conn.search(search_base=base, 
                search_filter='(cn='+username+')', 
                attributes=['cn','sn','givenName','fullName','ou','o'])
    print("User Details")
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