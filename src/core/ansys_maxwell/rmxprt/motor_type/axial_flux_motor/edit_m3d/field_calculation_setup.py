def field_calculation_setup(m3d):
    oModule = m3d.odesign.GetModule("FieldsReporter")
    
    oModule.EnterQty("B")
    oModule.XForm("Cylindrical", ["0mm", "0mm", "0mm"])
    oModule.CalcOp("ScalarX")
    oModule.AddNamedExpression("B_r", "Fields", 
    	[
    		"Fundamental_Quantity:=", ["B"],
    		"Vector_Function:="	, [			"FuncValueX:="		, "0mm",			"FuncValueY:="		, "0mm",			"FuncValueZ:="		, "0mm"],
    		"Operation:="		, ["ToCylindrical"],
    		"Operation:="		, ["ScalarX"]
    	])
        
    oModule.EnterQty("B")
    oModule.XForm("Cylindrical", ["0mm", "0mm", "0mm"])
    oModule.CalcOp("ScalarY")
    oModule.AddNamedExpression("B_t", "Fields", 
    	[
    		"Fundamental_Quantity:=", ["B"],
    		"Vector_Function:="	, [			"FuncValueX:="		, "0mm",			"FuncValueY:="		, "0mm",			"FuncValueZ:="		, "0mm"],
    		"Operation:="		, ["ToCylindrical"],
    		"Operation:="		, ["ScalarY"]
    	])
        
    oModule.EnterQty("B")
    oModule.XForm("Cylindrical", ["0mm", "0mm", "0mm"])
    oModule.CalcOp("ScalarZ")
    oModule.AddNamedExpression("B_z", "Fields", 
    	[
    		"Fundamental_Quantity:=", ["B"],
    		"Vector_Function:="	, [			"FuncValueX:="		, "0mm",			"FuncValueY:="		, "0mm",			"FuncValueZ:="		, "0mm"],
    		"Operation:="		, ["ToCylindrical"],
    		"Operation:="		, ["ScalarZ"]
    	])
        
    return True