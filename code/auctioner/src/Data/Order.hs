module Data.Order (Order (..), Side (..)) where

import Data.UUID (UUID)

data Side = Buy | Sell

data Order = Order
  { orderId :: UUID,
    side :: Side,
    quantity :: Int,
    price :: Int
  }