import { Link, Outlet } from "react-router-dom";
import { Tab, TabGroup, TabList, TabPanel, TabPanels } from '@headlessui/react'
import { NavBar } from "./components/NavBar";
import { Center, Circle, Square } from "@chakra-ui/react"

function App() {
  return (
    <div>
      <Center  h="180px" >
        <NavBar />
      </Center>
      <Outlet />
    </div>
  );
}

export default App;
