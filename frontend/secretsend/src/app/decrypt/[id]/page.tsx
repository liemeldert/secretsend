'use client'

import { useState } from 'react';
import { Center, SegmentedControl, Box, Card, Paper, Title, Stack } from '@mantine/core';
import React from 'react';

export default function DecryptPage({ params }: { params: { id: string } }) {
  const [selected, setSelected] = useState('simple');

  return (
    <Center p="md" m="md">        
        <Paper shadow="xs" radius="lg" p="md" w="75%">
            <Box align="center">
                
            </Box>
        </Paper>
    </Center>
  );
}