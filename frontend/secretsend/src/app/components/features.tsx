import {
    createStyles,
    Badge,
    Group,
    Title,
    Text,
    Card,
    SimpleGrid,
    Container,
    rem,
  } from '@mantine/core';
  import { IconGauge, IconUser, IconCookie, IconLock, IconBrandOpenSource } from '@tabler/icons-react';
  
  const data = [
    {
      title: 'Quick to use',
      description:
        'We securely generate a key for you to use, which is embedded into the url automatically. To the reciever, all they need to do is click the link.',
      icon: IconGauge,
    },
    {
      title: 'Highly secure',
      description:
        'We use millitary grade AES-256 encryption to ensure that your data is safe. We also use a key that is generated on the fly, so that it is never stored on our servers.',
      icon: IconLock,
    },
    {
      title: 'Open source',
      description:
        'Don&apos;t trust us? Anyone can view and contribute to our code, so you can be sure that we are not doing anything shady.',
      icon: IconBrandOpenSource,
    },
  ];
  
  const useStyles = createStyles((theme) => ({
    title: {
      fontSize: rem(34),
      fontWeight: 900,
  
      [theme.fn.smallerThan('sm')]: {
        fontSize: rem(24),
      },
    },
  
    description: {
      maxWidth: 600,
      margin: 'auto',
  
      '&::after': {
        content: '""',
        display: 'block',
        backgroundColor: theme.fn.primaryColor(),
        width: rem(45),
        height: rem(2),
        marginTop: theme.spacing.sm,
        marginLeft: 'auto',
        marginRight: 'auto',
      },
    },
  
    card: {
      border: `${rem(1)} solid ${
        theme.colorScheme === 'dark' ? theme.colors.dark[5] : theme.colors.gray[1]
      }`,
    },
  
    cardTitle: {
      '&::after': {
        content: '""',
        display: 'block',
        backgroundColor: theme.fn.primaryColor(),
        width: rem(45),
        height: rem(2),
        marginTop: theme.spacing.sm,
      },
    },
  }));
  
  export function FeaturesCards() {
    const { classes, theme } = useStyles();
    const features = data.map((feature) => (
      <Card key={feature.title} shadow="md" radius="md" className={classes.card} padding="xl">
        <feature.icon size={rem(50)} stroke={2} color={theme.fn.primaryColor()} />
        <Text fz="lg" fw={500} className={classes.cardTitle} mt="md">
          {feature.title}
        </Text>
        <Text fz="sm" c="dimmed" mt="sm">
          {feature.description}
        </Text>
      </Card>
    ));
  
    return (
      <Container size="lg" py="xl">
        {/* <Group position="center">
          <Badge variant="filled" size="lg">
            
          </Badge>
        </Group> */}
  
        <Title order={2} className={classes.title} ta="center" mt="sm">
          Designed for security.
        </Title>
  
        {/* <Text c="dimmed" className={classes.description} ta="center" mt="md">
          Every once in a while, you’ll see a Golbat that’s missing some fangs. This happens when
          hunger drives it to try biting a Steel-type Pokémon.
        </Text> */}
  
        <SimpleGrid cols={3} spacing="xl" mt={50} breakpoints={[{ maxWidth: 'md', cols: 1 }]}>
          {features}
        </SimpleGrid>
      </Container>
    );
  }