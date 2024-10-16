'use client'
// client rendering is a must since the encryption must happen in browser as to prevent sending
// passwords to the server without the secure encryption
import { useState } from 'react';
import { Center, SegmentedControl, Box, Card, Paper, Title, Stack } from '@mantine/core';
import Encrypt from './encrypt_form';

export default function EncryptCard() {
  const [selected, setSelected] = useState('simple');

  const handleSelection = (value: string) => {
    setSelected(value);
  };

  return (
    <Center p="md" m="md">        
        <Paper shadow="xs" radius="lg" p="md" w="75%">
            <Box align="center">
                <SegmentedControl
                    data={[
                    {
                        value: 'simple',
                        label: (
                        <Center>
                            <Box ml={10}>Simple</Box>
                        </Center>
                        ),
                    },
                    {
                        value: 'advanced',
                        label: (
                        <Center>
                            <Box ml={10}>Custom Password</Box>
                        </Center>
                        ),
                    },
                    ]}
                    value={selected}
                    onChange={handleSelection}
                />
            </Box>
            {selected === 'simple' && (
                <Encrypt />
            )}
            {selected === 'advanced' && (
                <Box>This is the custom password component</Box>
            )}
        </Paper>
    </Center>
  );
}