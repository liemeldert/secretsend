import { useState } from 'react';
import { Box, Button, Modal, Text } from '@mantine/core';

export default function DisclaimerModal() {
  const [open, setOpen] = useState(false);

  const handleAgree = () => {
    // Handle user agreement here
    setOpen(false);
  };

  return (
    <Box>
      <Button onClick={() => setOpen(true)}>Proceed</Button>
      <Modal
        opened={open}
        onClose={() => setOpen(false)}
        title="Disclaimer"
        size="sm"
        padding="lg"
        overlayOpacity={0.7}
      >
        <Text>
          By proceeding, you agree to the terms of service and confirm that you will not use this
          application in violation of the law.
        </Text>
        <Box mt="lg">
          <Button onClick={handleAgree}>I Agree</Button>
        </Box>
      </Modal>
    </Box>
  );
}