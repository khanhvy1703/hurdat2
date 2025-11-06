"use client";

import { useEffect, useState } from "react";
import {
  Box,
  Spinner,
  Text,
  Table,
  ButtonGroup,
  IconButton,
  Pagination,
  Stack,
  Button,
  HStack,
} from "@chakra-ui/react";
import { LuChevronLeft, LuChevronRight } from "react-icons/lu";

export type Hurricane = {
  name: string;
  year: number;
  month: number;
  day: string;
  wind: number;
  latitude: number;
  longitude: number;
};

export default function Home() {
  const [hurricanes, setHurricanes] = useState<Hurricane[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<boolean>(false);
  const [errorMessage, setErrorMessage] = useState<string>("");
  const [page, setPage] = useState<number>(1);
  const [exported, setExported] = useState<boolean>(false);

  useEffect(() => {
    const fetchHurricanes = async () => {
      try {
        const response = await fetch(
          `${process.env.NEXT_PUBLIC_SERVER_ENDPOINT}/hurricanes/landfall/florida`
        );
        if (!response.ok) {
          setError(true);
          return;
        }

        const data = await response.json();

        if (!data || !data.success) {
          setError(data.error || "Invalid API response format.");
          return;
        }

        setHurricanes(data.data);
      } catch (error) {
        setError(true);
        setErrorMessage("Failed to fetch hurricane data.");
      } finally {
        setLoading(false);
      }
    };

    fetchHurricanes();
  }, []);

  const exportToCSV = async () => {
    setLoading(true);
    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_SERVER_ENDPOINT}/export_csv`,
        {
          method: "GET",
        }
      );

      if (!response.ok) {
        setError(true);
        setErrorMessage(`HTTP error: ${response.status}`);
        return;
      }

      const data = await response.json();

      if (!data || !data.success) {
        setError(data.error || "Invalid API response format.");
        return;
      }

      setExported(true);
    } catch (error) {
      setError(true);
      setErrorMessage(`Failed to export CSV.`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box
      minH="100vh"
      bg="white"
      color="black"
      display="flex"
      flexDirection="column"
      alignItems="center"
      justifyContent="flex-start"
      py={10}
    >
      {loading && <Spinner size="xl" mt={10} />}
      {error && <Text fontSize="xl">{errorMessage}</Text>}
      {hurricanes.length <= 0 && !loading && (
        <Text fontSize="xl">No hurricanes found</Text>
      )}

      {hurricanes.length > 0 && !loading && !error && (
        <>
          <Text fontSize="3xl" fontWeight="bold" textAlign="center" mb={6}>
            All hurricanes that have made landfall in Florida since 1900
          </Text>

          <HStack mb={6}>
            <Button colorPalette="blue" variant="solid" onClick={exportToCSV}>
              Export To CSV
            </Button>
            {exported && (
              <Text fontSize="md" color="green.500">
                CSV exported successfully!
              </Text>
            )}
          </HStack>

          <Box w={{ base: "100%", md: "80%", lg: "50%" }} mx="auto">
            <Stack width="full" gap="5">
              <Table.Root size="sm" variant="outline" showColumnBorder>
                <Table.Header>
                  <Table.Row>
                    <Table.ColumnHeader w="34%">Name</Table.ColumnHeader>
                    <Table.ColumnHeader textAlign="center" w="33%">
                      Date
                    </Table.ColumnHeader>
                    <Table.ColumnHeader textAlign="end" w="33%">
                      Wind Speed
                    </Table.ColumnHeader>
                  </Table.Row>
                </Table.Header>

                <Table.Body>
                  {hurricanes
                    .slice((page - 1) * 10, page * 10)
                    .map((hurricane, index) => (
                      <Table.Row key={index}>
                        <Table.Cell fontWeight="medium">
                          {hurricane.name}
                        </Table.Cell>
                        <Table.Cell textAlign="center">
                          {hurricane.month}/{hurricane.day}/{hurricane.year}
                        </Table.Cell>
                        <Table.Cell textAlign="end">
                          {hurricane.wind}
                        </Table.Cell>
                      </Table.Row>
                    ))}
                </Table.Body>
              </Table.Root>

              <Pagination.Root
                count={Math.ceil(hurricanes.length / 10) * 10}
                pageSize={10}
                page={page}
                onPageChange={(e) => setPage(e.page)}
              >
                <ButtonGroup
                  display="flex"
                  justifyContent="center"
                  alignItems="center"
                  gap={2}
                  mt={6}
                >
                  <Pagination.PrevTrigger asChild>
                    <IconButton
                      aria-label="Previous page"
                      color="black"
                      variant="ghost"
                      _hover={{ bg: "gray.100" }}
                    >
                      <LuChevronLeft />
                    </IconButton>
                  </Pagination.PrevTrigger>

                  <Pagination.Items
                    render={(pageItem) => (
                      <IconButton
                        key={pageItem.value}
                        aria-label={`Page ${pageItem.value}`}
                        color="black"
                        borderWidth={page === pageItem.value ? "2px" : "1px"}
                        borderColor={
                          page === pageItem.value ? "black" : "gray.200"
                        }
                        bg={page === pageItem.value ? "gray.100" : "white"}
                        fontWeight={page === pageItem.value ? "bold" : "normal"}
                        _hover={{ bg: "gray.50" }}
                        onClick={() => setPage(pageItem.value)}
                      >
                        {pageItem.value}
                      </IconButton>
                    )}
                  />

                  <Pagination.NextTrigger asChild>
                    <IconButton
                      aria-label="Next page"
                      color="black"
                      variant="ghost"
                      _hover={{ bg: "gray.100" }}
                    >
                      <LuChevronRight />
                    </IconButton>
                  </Pagination.NextTrigger>
                </ButtonGroup>
              </Pagination.Root>
            </Stack>
          </Box>
        </>
      )}
    </Box>
  );
}
