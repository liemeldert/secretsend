"use client"
import { Box, Space, Stack, Title, rem, createStyles } from '@mantine/core'
import { SiteHeader } from './components/header'
import EncryptCard from './encrypt/encrypt_card'
import {  HomepageHero } from './components/homepage_hero'
import { FooterLinks } from './components/footer'
import { FeaturesCards } from './components/features'
import { useTheme } from '@emotion/react'

const useStyles = createStyles((theme) => ({  
  title: {
    textAlign: 'center',
    fontWeight: 800,
    fontSize: rem(40),
    letterSpacing: -1,
    color: theme.colorScheme === 'dark' ? theme.white : theme.black,
    marginBottom: theme.spacing.xs,
    fontFamily: `Greycliff CF, ${theme.fontFamily}`,

    [theme.fn.smallerThan('xs')]: {
      fontSize: rem(28),
      textAlign: 'left',
    },
  },
  highlight: {
    color: theme.colors[theme.primaryColor][theme.colorScheme === 'dark' ? 4 : 6],
  }, 
}));

export default function Home() {

  const theme = useStyles();

  return (
    <Box>
      <HomepageHero /> 
      <Box style={{
        background: '#f0f0f0',
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        minHeight: 'calc(100vh - 200px)',
        marginBottom: '0',
      }}>
        <FeaturesCards />
      </Box>

      <Space m="xl" h="xl" />
    
      <Box style={{
        // background: 'linear-gradient(to bottom, #7b4397, #dc2430)',
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        // minHeight: 'calc(100vh - 200px)',  
        marginBottom: '0',
      }}>
        <Stack>
            <div className="#send">
              <Title className={theme.highlight} inherit align="center" >Securely Send a Password</Title>
            </div>
          <EncryptCard />
        </Stack>
      </Box>
    </Box>
  )
}
