SMELLS_DICT = {
    "S103": {
        "label": "Lengthy Line",
        "short_label": "LL",
        "description": "Lines should not be too long",
    },
    "S107": {
        "label": "Long Parameter List",
        "short_label": "LPL",
        "description": "Functions should not have too many parameters",
    },
    "S134": {
        "label": "Depth",
        "short_label": "D",
        "description": "Control flow statements 'if', 'for', 'while', 'switch' and 'try' should not be nested too deeply",
    },
    "S138": {
        "label": "Long Method",
        "short_label": "LM",
        "description": "Functions should not have too many lines of code",
    },
    "S1121": {
        "label": "Assignment in Conditional Statement",
        "short_label": "ACS",
        "description": "Assignments should not be made from within sub-expressions",
    },
    "S1479": {
        "label": "Complex Switch Case",
        "short_label": "CSC",
        "description": "'switch' statements should not have too many 'case' clauses",
    },
    "S1541": {
        "label": "Complex Code",
        "short_label": "CC",
        "description": "Cyclomatic Complexity of functions should not be too high",
    },
    # Only TS
    #"S4327": {
    #    "label": "This-Assign",
    #    "short_label": "TA",
    #    "description": "'this' should not be assigned to variables",
    #},

    # Additions
    "S104": {
        "label": "Lengthy File",
        "short_label": "LF",
        "description": "Files should not have too many lines of code",
    },
    "S109": {
        "label": "Magic Number",
        "short_label": "MN",
        "description": "Magic numbers should not be used",
    },
    "S125": {
        "label": "Retired Code",
        "short_label": "RC",
        "description": "Sections of code should not be commented out",
    },
    "S1067": {
        "label": "Complex Expression",
        "short_label": "CE",
        "description": "Expressions should not be too complex",
    },
    "S1117": {
        "label": "Shadowed Variable",
        "short_label": "SV",
        "description": "Variables should not be shadowed",
    },
    "S1186": {
        "label": "Empty Function",
        "short_label": "EF",
        "description": "Functions should not be empty",
    },
    "S1192": {
        "label": "Duplicated String",
        "short_label": "DS",
        "description": "String literals should not be duplicated",
    },
    "S1440": {
        "label": "Weak Equality",
        "short_label": "WE",
        "description": "'===' and '!==' should be used instead of '==' and '!='",
    },
    "S1763": {
        "label": "Unreachable Code",
        "short_label": "UC",
        "description": "All code should be reachable",
    },
    "S1854": {
        "label": "Useless Assignment",
        "short_label": "UA",
        "description": "Unused assignments should be removed",
    },
    "S2424": {
        "label": "Overwritten Built-Ins",
        "short_label": "OBI",
        "description": "Built-in objects should not be overridden",
    },
    "S2814": {
        "label": "Overwritten Variable/Function",
        "short_label": "OVF",
        "description": "Variables and functions should not be redeclared",
    },
    "S3003": {
        "label": "Ordinal String Comparison",
        "short_label": "OSC",
        "description": "Comparison operators should not be used with strings",
    },
    "S3516": {
        "label": "Invariant Function",
        "short_label": "IF",
        "description": "Function returns should not be invariant",
    },
    "S3696": {
        "label": "Invalid Error",
        "short_label": "IE",
        "description": "Literals should not be thrown",
    },
    "S3699": {
        "label": "Unknown Output",
        "short_label": "UO",
        "description": "The output of functions that don't return anything should not be used",
    },
    "S3801": {
        "label": "Inconsistent Return",
        "short_label": "IR",
        "description": "Functions should use 'return' consistently",
    },
    "S4144": {
        "label": "Duplicated Function",
        "short_label": "DF",
        "description": "Functions should not have identical implementations",
    },
}

SMELLS = list(SMELLS_DICT.keys())
N_SMELLS = len(SMELLS)