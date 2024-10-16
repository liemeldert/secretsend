import { useState } from 'react';
import { Box, Button, Checkbox, LoadingOverlay, Select, TextInput } from '@mantine/core';
import { DateTimePicker } from '@mantine/dates';
import { useForm } from '@mantine/form';
import axios from 'axios';
import Turnstile from 'react-turnstile';
import { useConfig } from '../config/useConfig';
import { EncryptedString } from '@/utils/EncryptedString';

export default function Encrypt() {
  const [selected, setSelected] = useState('preview');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState<string | null>(null);
  const [timeType, setTimeType] = useState('date');
  const [Token, setToken] = useState('');

  const [config, configLoading] = useConfig();

  const form = useForm({
    initialValues: {
      password: '',
      termsOfService: false,
      expiryTime: '',
      token: '',
    },
  });

  const handleSubmit = async (values: { password: string; expiryTime: any; }) => {
    setLoading(true);
    setError(null);
    setResult(null);

    const encryptedString = new EncryptedString(values.password);

    try {
      const response = await axios.post(
        `${config?.backend_url}/v1/public/`,
        {
          content: encryptedString.encryptedPassword,
          expiry_time: values.expiryTime,
          turnstile_response: Token,
        },
        {
          params: {
            key: encryptedString.key,
          },
        }
      );

      setResult(encryptedString.generateLink(response.data.id));
    } catch (error) {
      setError(error.message);
    } finally {
      setLoading(false);
    }
  };

  const handleSelection = (value: string) => {
    setSelected(value);
  };

  const handleTimeTypeChange = (value: string) => {
    setTimeType(value);
  };

  return (
    <Box mb={20} pos="relative">
      <form onSubmit={form.onSubmit(handleSubmit)}>
        <TextInput
          label="Password"
          {...form.getInputProps('password')}
        />
        <Select
          label="Expiry Time Type"
          data={[
            // Add your options here
          ]}
          value={timeType}
          onChange={handleTimeTypeChange}
        />
        {/* Add other form fields here */}
        <Button type="submit" disabled={loading}>
          {loading ? 'Encrypting...' : 'Encrypt'}
        </Button>
      </form>
      {error && <div>Error: {error}</div>}
      {result && <div>Result: {result}</div>}
    </Box>
  );
}