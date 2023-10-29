/Applications/anaconda3/API/bin/python /Users/zhangzhiyang/学习文件/Code/API/test.py 

################################################################################
Start to get variable node: 
<String>.input
<String>.str
<int>.length
<String>.output
<boolean>.contains
<int>.index
<Timestamp>.priceDate
<String>.dateStr
<StringBuilder>.sb
<StringBuffer>.sf
<int>.retValue
<String>.sql
<PreparedStatement>.pstmt
<ResultSet>.rs
<Timestamp>.plDate

################################################################################
Start to get API node: 
String.toUpperCase()  invoker:input  receiver:None
String.reversed()  invoker:input  receiver:None
String.length()  invoker:input  receiver:None
String.toUpperCase()  invoker:input  receiver:None
String.contains("o")  invoker:input  receiver:None
String.indexOf("W")  invoker:input  receiver:None
Env.getContext(Env.getCtx(), p_WindowNo, "DateOrdered")  invoker:Env  receiver:None
Env.getCtx()  invoker:Env  receiver:None
String.length()  invoker:dateStr  receiver:None
Env.getContextAsDate(Env.getCtx(), p_WindowNo, "DateOrdered")  invoker:Env  receiver:None
Env.getCtx()  invoker:Env  receiver:None
Env.getContext(Env.getCtx(), p_WindowNo, "DateInvoiced")  invoker:Env  receiver:None
Env.getCtx()  invoker:Env  receiver:None
String.length()  invoker:dateStr  receiver:None
Env.getContextAsDate(Env.getCtx(), p_WindowNo, "DateInvoiced")  invoker:Env  receiver:None
Env.getCtx()  invoker:Env  receiver:None
System.currentTimeMillis()  invoker:System  receiver:None
log.config("M_PriceList_ID=" + M_PriceList_ID + " - " + priceDate)  invoker:log  receiver:None
DB.prepareStatement(sql, null)  invoker:DB  receiver:None
PreparedStatement.setInt(1, M_PriceList_ID)  invoker:pstmt  receiver:None
PreparedStatement.executeQuery()  invoker:pstmt  receiver:None
ResultSet.next()  invoker:rs  receiver:None
ResultSet.getTimestamp(2)  invoker:rs  receiver:None
Timestamp.before(plDate)  invoker:priceDate  receiver:None
ResultSet.getInt(1)  invoker:rs  receiver:None
ResultSet.close()  invoker:rs  receiver:None
PreparedStatement.close()  invoker:pstmt  receiver:None
log.log(Level.SEVERE, sql, e)  invoker:log  receiver:None
Env.setContext(Env.getCtx(), p_WindowNo, "M_PriceList_Version_ID", retValue)  invoker:Env  receiver:None
Env.getCtx()  invoker:Env  receiver:None

################################################################################
Print invoker edge: 
String.toUpperCase()#invoker:input#receiver:None   <String>.input
String.reversed()#invoker:input#receiver:None   <String>.input
String.length()#invoker:input#receiver:None   <String>.input
String.toUpperCase()#invoker:input#receiver:None   <String>.input
String.contains("o")#invoker:input#receiver:None   <String>.input
String.indexOf("W")#invoker:input#receiver:None   <String>.input
Env.getContext(Env.getCtx(), p_WindowNo, "DateOrdered")#invoker:Env#receiver:None   <Object>.Env
Env.getCtx()#invoker:Env#receiver:None   <Object>.Env
String.length()#invoker:dateStr#receiver:None   <String>.dateStr
Env.getContextAsDate(Env.getCtx(), p_WindowNo, "DateOrdered")#invoker:Env#receiver:None   <Object>.Env
Env.getCtx()#invoker:Env#receiver:None   <Object>.Env
Env.getContext(Env.getCtx(), p_WindowNo, "DateInvoiced")#invoker:Env#receiver:None   <Object>.Env
Env.getCtx()#invoker:Env#receiver:None   <Object>.Env
String.length()#invoker:dateStr#receiver:None   <String>.dateStr
Env.getContextAsDate(Env.getCtx(), p_WindowNo, "DateInvoiced")#invoker:Env#receiver:None   <Object>.Env
Env.getCtx()#invoker:Env#receiver:None   <Object>.Env
System.currentTimeMillis()#invoker:System#receiver:None   <Object>.System
log.config("M_PriceList_ID=" + M_PriceList_ID + " - " + priceDate)#invoker:log#receiver:None   <Object>.log
DB.prepareStatement(sql, null)#invoker:DB#receiver:None   <Object>.DB
PreparedStatement.setInt(1, M_PriceList_ID)#invoker:pstmt#receiver:None   <PreparedStatement>.pstmt
PreparedStatement.executeQuery()#invoker:pstmt#receiver:None   <PreparedStatement>.pstmt
ResultSet.next()#invoker:rs#receiver:None   <ResultSet>.rs
ResultSet.getTimestamp(2)#invoker:rs#receiver:None   <ResultSet>.rs
Timestamp.before(plDate)#invoker:priceDate#receiver:None   <Timestamp>.priceDate
ResultSet.getInt(1)#invoker:rs#receiver:None   <ResultSet>.rs
ResultSet.close()#invoker:rs#receiver:None   <ResultSet>.rs
PreparedStatement.close()#invoker:pstmt#receiver:None   <PreparedStatement>.pstmt
log.log(Level.SEVERE, sql, e)#invoker:log#receiver:None   <Object>.log
Env.setContext(Env.getCtx(), p_WindowNo, "M_PriceList_Version_ID", retValue)#invoker:Env#receiver:None   <Object>.Env
Env.getCtx()#invoker:Env#receiver:None   <Object>.Env
dict_keys(['input', 'str', 'length', 'output', 'contains', 'index', 'priceDate', 'dateStr', 'sb', 'sf', 'retValue', 'sql', 'pstmt', 'rs', 'plDate'])
dict_keys(['String.toUpperCase()#invoker:input#receiver:None', 'String.reversed()#invoker:input#receiver:None', 'String.length()#invoker:input#receiver:None', 'String.contains("o")#invoker:input#receiver:None', 'String.indexOf("W")#invoker:input#receiver:None', 'Env.getContext(Env.getCtx(), p_WindowNo, "DateOrdered")#invoker:Env#receiver:None', 'Env.getCtx()#invoker:Env#receiver:None', 'String.length()#invoker:dateStr#receiver:None', 'Env.getContextAsDate(Env.getCtx(), p_WindowNo, "DateOrdered")#invoker:Env#receiver:None', 'Env.getContext(Env.getCtx(), p_WindowNo, "DateInvoiced")#invoker:Env#receiver:None', 'Env.getContextAsDate(Env.getCtx(), p_WindowNo, "DateInvoiced")#invoker:Env#receiver:None', 'System.currentTimeMillis()#invoker:System#receiver:None', 'log.config("M_PriceList_ID=" + M_PriceList_ID + " - " + priceDate)#invoker:log#receiver:None', 'DB.prepareStatement(sql, null)#invoker:DB#receiver:None', 'PreparedStatement.setInt(1, M_PriceList_ID)#invoker:pstmt#receiver:None', 'PreparedStatement.executeQuery()#invoker:pstmt#receiver:None', 'ResultSet.next()#invoker:rs#receiver:None', 'ResultSet.getTimestamp(2)#invoker:rs#receiver:None', 'Timestamp.before(plDate)#invoker:priceDate#receiver:None', 'ResultSet.getInt(1)#invoker:rs#receiver:None', 'ResultSet.close()#invoker:rs#receiver:None', 'PreparedStatement.close()#invoker:pstmt#receiver:None', 'log.log(Level.SEVERE, sql, e)#invoker:log#receiver:None', 'Env.setContext(Env.getCtx(), p_WindowNo, "M_PriceList_Version_ID", retValue)#invoker:Env#receiver:None'])

################################################################################
Print receiver edge: 
String.toUpperCase()#invoker:input#receiver:None   <String>.str
Env.getContextAsDate(Env.getCtx(), p_WindowNo, "DateOrdered")#invoker:Env#receiver:None   <Timestamp>.priceDate
Env.getContext(Env.getCtx(), p_WindowNo, "DateInvoiced")#invoker:Env#receiver:None   <String>.dateStr
Env.getContextAsDate(Env.getCtx(), p_WindowNo, "DateInvoiced")#invoker:Env#receiver:None   <Timestamp>.priceDate
ResultSet.getInt(1)#invoker:rs#receiver:None   <int>.retValue
String.length()#invoker:input#receiver:None   <int>.length
String.toUpperCase()#invoker:input#receiver:None   <String>.output
String.contains("o")#invoker:input#receiver:None   <boolean>.contains
String.indexOf("W")#invoker:input#receiver:None   <int>.index
Env.getContext(Env.getCtx(), p_WindowNo, "DateOrdered")#invoker:Env#receiver:None   <String>.dateStr
DB.prepareStatement(sql, null)#invoker:DB#receiver:None   <PreparedStatement>.pstmt
PreparedStatement.executeQuery()#invoker:pstmt#receiver:None   <ResultSet>.rs
ResultSet.getTimestamp(2)#invoker:rs#receiver:None   <Timestamp>.plDate

进程已结束,退出代码0
