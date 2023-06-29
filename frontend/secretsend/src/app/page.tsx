"use client"
import { Box, Title } from '@mantine/core'
import { SiteHeader } from './components/header'
import EncryptCard from './encrypt/encrypt_card'
import {  HomepageHero } from './components/homepage_hero'

export default function Home() {
  return (
    <Box>
      <SiteHeader />
      <HomepageHero />
      <EncryptCard />
    </Box>
  )
}
