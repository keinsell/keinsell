# ini-parser

```
FUNCTION ParseINI(filePath):
    DECLARE iniData AS Dictionary

    OPEN filePath FOR READING AS file
    DECLARE currentSection AS STRING = ""

    WHILE NOT END OF file:
        DECLARE line AS READ LINE FROM file
        line = TRIM(line)

        IF line IS EMPTY OR line STARTS WITH ";" THEN
            CONTINUE

        IF line STARTS WITH "[" AND line ENDS WITH "]" THEN
            currentSection = REMOVE BRACKETS(line)
            iniData[currentSection] = NEW Dictionary
            CONTINUE

        IF currentSection IS NOT EMPTY THEN
            DECLARE keyValue AS SPLIT(line, "=")
            IF LENGTH(keyValue) == 2 THEN
                DECLARE key AS TRIM(keyValue[0])
                DECLARE value AS TRIM(keyValue[1])
                iniData[currentSection][key] = value

    CLOSE file
    RETURN iniData
```
