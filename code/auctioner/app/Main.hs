module Main where

import Data.Order (Order (Order), OrderSide (Buy))

main :: IO ()
main = do
  putStrLn "-- AUCTIONER --"
  print Order ("adasd" 1 Buy 1)
