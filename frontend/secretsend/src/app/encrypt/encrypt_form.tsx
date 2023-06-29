import { useState } from 'react';
import { Box, Button, Checkbox, Select, TextInput } from '@mantine/core';
import { DateTimePicker } from '@mantine/dates';
import { useForm } from '@mantine/form';
import CryptoJS from 'crypto-js';
import axios from 'axios';
import Turnstile from 'react-turnstile';

export default function Encrypt() {
  const [selected, setSelected] = useState('preview');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);
  const [timeType, setTimeType] = useState('date');
  const [Token, setToken] = useState('');

  const form = useForm({
    initialValues: {
      password: '',
      termsOfService: false,
      expiryTime: '',
      token: '',
    },
    onSubmit: async (values: { password: string; expiryTime: any; }) => {
      setLoading(true);
      setError(null);
      setResult(null);

      const key = generateKey();
      const encryptedPassword = encryptPassword(values.password, key);

      try {
        const response = await axios.post(
          'https://ssapi.liem.zip/publicv1/',
          {
            content: encryptedPassword,
            expiry_time: values.expiryTime,
            turnstile_response: Token,
          },
          {
            params: {
              key: key,
            },
          }
        );

        setResult(`https://send.liem.zip/get/${response.data.id}/${key}`);
      } catch (error) {
        setError(error.message);
      } finally {
        setLoading(false);
      }
    },
  });


  const handleSelection = (value: string) => {
    setSelected(value);
  };

  const handleTimeTypeChange = (value: string) => { // Handle timeType change
    setTimeType(value);
  };

  const generateKey = () => {
    const characters =
      'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_';
    const length = 64;
    let result = '';
    for (let i = 0; i < length; i++) {
      result += characters.charAt(Math.floor(Math.random() * characters.length));
    }
    return result;
  };

  const encryptPassword = (password: string, key: string) => {
    return CryptoJS.AES.encrypt(password, key).toString();
  };

  return (
    <form onSubmit={form.onSubmit}>
      <Box mb={20}>
        <TextInput
          label="Password"
          {...form.getInputProps('password')}
        />
        <Select
          label="Expiry Time Type"
          data={[
            { value: 'date', label: 'Specific Date' },
            { value: 'relative', label: 'Relative Time' },
          ]}
          value={timeType}
          onChange={handleTimeTypeChange}
        />
        {timeType === 'date' ? (
          <DateTimePicker
            label="Expiry Date"
            {...form.getInputProps('expiryTime')}
          />
        ) : (
          <Select
            label="Expiry Time"
            name="expiryTime"
            data={[
              { value: '60', label: '1 Hour' },
              { value: '1440', label: '1 Day' },
              // Add more options as needed...
            ]}
            {...form.getInputProps('expiryTime')}
          />
        )}
        <Turnstile sitekey='' onVerify={(token) => setToken(token)} />
        <Checkbox
          mt="md"
          label="I agree to the Terms of Service and confirm that I will not use this application in violation of the law."
          {...form.getInputProps('termsOfService', { type: 'checkbox' })}
        />
      </Box>
      <Button type="submit" disabled={loading}>
        {loading ? 'Loading...' : 'Submit'}
      </Button>
      {error && <Box mt={20}>{error}</Box>}
      {result && <Box mt={20}>{result}</Box>}
    </form>
  );
}
