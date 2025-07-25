module Lib
    ( parseIniLines
    ) where

someFunc :: IO ()
someFunc = putStrLn "someFunc"

type Record = (String, String)
type Selection = [Record]
type IniData = [Selection]

data Line = Comment | Empty | Selection | Record

parseIniLines :: [String] -> IniData
parseIniLines lines = []
